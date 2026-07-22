import { expect, test, type Page } from '@playwright/test'

type Locale = 'fr' | 'en' | 'de'

function makeMembership(locale: Locale, role: string) {
  return {
    tenant_id: 'tenant-demo-1',
    slug: 'demo',
    name: 'Combis Sport Verein',
    default_language: locale,
    roles: [role],
    branding: {
      primary_color: '#1f4f8f',
      logo_url: '',
    },
    modules: {
      membership: true,
      contributions: true,
      policies: true,
      disciplinary: true,
      events: true,
      announcements: true,
      chat: true,
      notifications: true,
    },
    profile_type: role === 'member' ? 'member' : role === 'principal_admin' ? 'admin' : 'staff',
  }
}

function makeMe(locale: Locale, role: string) {
  return {
    id: `user-${role}-1`,
    email: `${role}@demo.org`,
    display_name: role === 'member' ? 'Aude Ndam' : role === 'secretary_general' ? 'Sophie Mvondo' : 'Lukas Fischer',
    preferred_language: locale,
    status: 'active',
    tenant_id: 'tenant-demo-1',
    roles: [role],
    last_login_at: null,
    memberships: [makeMembership(locale, role)],
  }
}

function statementResponse(locale: Locale) {
  return {
    profile: {
      id: 'profile-1',
      tenant_id: 'tenant-demo-1',
      user_id: 'user-member-1',
      member_code: 'MEM-1001',
      first_name: locale === 'de' ? 'Anna' : locale === 'en' ? 'Ava' : 'Awa',
      last_name: locale === 'de' ? 'Meyer' : locale === 'en' ? 'Brown' : 'Ngono',
      display_name: locale === 'de' ? 'Anna Meyer' : locale === 'en' ? 'Ava Brown' : 'Awa Ngono',
      email: 'member@demo.org',
      phone: '+49 000 000',
      status: 'active',
      joined_at: '2025-01-10T10:00:00Z',
      created_at: '2025-01-10T10:00:00Z',
      updated_at: '2025-06-01T10:00:00Z',
    },
    summary: {
      profile: {
        id: 'profile-1',
        tenant_id: 'tenant-demo-1',
        user_id: 'user-member-1',
        member_code: 'MEM-1001',
        first_name: locale === 'de' ? 'Anna' : locale === 'en' ? 'Ava' : 'Awa',
        last_name: locale === 'de' ? 'Meyer' : locale === 'en' ? 'Brown' : 'Ngono',
        display_name: locale === 'de' ? 'Anna Meyer' : locale === 'en' ? 'Ava Brown' : 'Awa Ngono',
        email: 'member@demo.org',
        phone: '+49 000 000',
        status: 'active',
        joined_at: '2025-01-10T10:00:00Z',
        created_at: '2025-01-10T10:00:00Z',
        updated_at: '2025-06-01T10:00:00Z',
      },
      total_expected: '120.00',
      total_paid: '90.00',
      total_balance: '30.00',
      contribution_count: 2,
    },
    contributions: [
      {
        id: 'contrib-1',
        tenant_id: 'tenant-demo-1',
        membership_profile_id: 'profile-1',
        year: 2025,
        expected_amount: '60.00',
        paid_amount: '30.00',
        balance: '30.00',
        currency: 'EUR',
        status: 'partial',
        due_date: '2025-12-31T00:00:00Z',
      },
    ],
  }
}

async function seedLocale(page: Page, locale: Locale, role: string) {
  await page.addInitScript(({ nextLocale }) => {
    window.localStorage.setItem('preferred_locale', nextLocale)
    window.localStorage.setItem('access_token', 'playwright-access-token')
  }, { nextLocale: locale })

  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeMe(locale, role)),
    })
  })
}

test.describe('locale coverage', () => {
  test('member profile renders in the selected language', async ({ page }) => {
    await seedLocale(page, 'fr', 'member')
    await page.route('**/api/v1/memberships/me/statement', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(statementResponse('fr')),
      })
    })

    await page.goto('/members/profile')
    await expect(page.getByRole('heading', { name: 'Mon profil et mon relevé de cotisations' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Télécharger mon relevé' })).toBeVisible()
    await expect(page.getByText("Cet espace n'expose jamais les données financières d'un autre membre.")).toBeVisible()
  })

  test('member profile shows recovery state and retries after failure', async ({ page }) => {
    await seedLocale(page, 'fr', 'member')

    await page.addInitScript(() => {
      ;(window as any).__forceStatementError = true
    })

    await page.route('**/api/v1/memberships/me/statement', async (route) => {
      const shouldFail = await page.evaluate(() => (window as any).__forceStatementError === true)
      if (shouldFail) {
        await page.evaluate(() => {
          ;(window as any).__forceStatementError = false
        })
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Service indisponible' }) })
        return
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(statementResponse('fr')) })
    })

    await page.goto('/members/profile')
    const retryButton = page.getByRole('button', { name: 'Réessayer' })
    await expect(retryButton).toBeVisible({ timeout: 10000 })
    await expect(page.getByText("Espace indisponible")).toBeVisible()
    await retryButton.click()
    await expect(page.getByRole('heading', { name: 'Mon profil et mon relevé de cotisations' })).toBeVisible()
  })

  test('secretary workspace renders in English when requested', async ({ page }) => {
    await seedLocale(page, 'en', 'secretary_general')

    await page.goto('/secretary')
    await expect(page.getByRole('heading', { name: 'Official records and communication workspace' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Open documents' })).toBeVisible()
    await expect(page.getByText('Manage the documents, policies, and announcements that shape the formal life of the organization without entering finance or disciplinary operations.')).toBeVisible()
  })

  test('sports workspace renders in German when requested', async ({ page }) => {
    await seedLocale(page, 'de', 'sports_manager')
    await page.route('**/api/v1/sports/events', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      })
    })

    await page.goto('/sports')
    await expect(page.getByRole('heading', { name: 'Sportbereich' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Aktualisieren' })).toBeVisible()
    await expect(page.getByText('Noch keine Sportereignisse')).toBeVisible()
  })

  test('censor workspace shows recovery state and retries after failure', async ({ page }) => {
    await seedLocale(page, 'fr', 'censor')

    await page.addInitScript(() => {
      ;(window as any).__forceCensorError = true
    })

    await page.route('**/api/v1/disciplinary/records**', async (route) => {
      const shouldFail = await page.evaluate(() => (window as any).__forceCensorError === true)
      if (shouldFail) {
        await page.evaluate(() => {
          ;(window as any).__forceCensorError = false
        })
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Service indisponible' }) })
        return
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })

    await page.goto('/censor')
    const retryButton = page.getByRole('button', { name: 'Réessayer' })
    await expect(retryButton).toBeVisible({ timeout: 10000 })
    await expect(page.getByText("L'espace disciplinaire est indisponible")).toBeVisible()
    await retryButton.click()
    await expect(page.getByText('Aucun dossier disciplinaire')).toBeVisible()
  })

  test('sports workspace shows recovery state and retries after failure', async ({ page }) => {
    await seedLocale(page, 'de', 'sports_manager')

    await page.addInitScript(() => {
      ;(window as any).__forceSportsError = true
    })

    await page.route('**/api/v1/sports/events', async (route) => {
      const shouldFail = await page.evaluate(() => (window as any).__forceSportsError === true)
      if (shouldFail) {
        await page.evaluate(() => {
          ;(window as any).__forceSportsError = false
        })
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Service nicht verfügbar' }) })
        return
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })

    await page.goto('/sports')
    const retryButton = page.getByRole('button', { name: 'Erneut versuchen' })
    await expect(retryButton).toBeVisible({ timeout: 10000 })
    await expect(page.getByText('Sportbereich nicht verfügbar')).toBeVisible()
    await retryButton.click()
    await expect(page.getByText('Noch keine Sportereignisse')).toBeVisible()
  })

  test('auditor workspace shows recovery state and retries after failure', async ({ page }) => {
    await seedLocale(page, 'fr', 'auditor')

    await page.addInitScript(() => {
      ;(window as any).__forceAuditorError = true
    })

    await page.route('**/api/v1/memberships/', async (route) => {
      const shouldFail = await page.evaluate(() => (window as any).__forceAuditorError === true)
      if (shouldFail) {
        await page.evaluate(() => {
          ;(window as any).__forceAuditorError = false
        })
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Service indisponible' }) })
        return
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/contributions?year=*', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/contributions/summary**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_expected: '0.00',
          total_paid: '0.00',
          total_balance: '0.00',
          total_count: 0,
        }),
      })
    })
    await page.route('**/api/v1/contributions/payments', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })

    await page.goto('/finance-audit')
    const retryButton = page.getByRole('button', { name: 'Réessayer' })
    await expect(retryButton).toBeVisible({ timeout: 10000 })
    await expect(page.getByText("L'espace d'audit finances est indisponible")).toBeVisible()
    await retryButton.click()
    await expect(page.getByRole('heading', { name: 'Supervision financière en lecture seule' })).toBeVisible()
  })

  test('governance cockpit shows recovery state and retries after failure', async ({ page }) => {
    await seedLocale(page, 'fr', 'president')

    await page.addInitScript(() => {
      ;(window as any).__forceGovernanceError = true
    })

    await page.route('**/api/v1/documents', async (route) => {
      const shouldFail = await page.evaluate(() => (window as any).__forceGovernanceError === true)
      if (shouldFail) {
        await page.evaluate(() => {
          ;(window as any).__forceGovernanceError = false
        })
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Service indisponible' }) })
        return
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/announcements/active', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/events/public', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/memberships/', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/contributions/summary', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_expected: '0.00',
          total_paid: '0.00',
          total_balance: '0.00',
          total_count: 0,
        }),
      })
    })
    await page.route('**/api/v1/admin/audit-events**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })

    await page.goto('/governance')
    const retryButton = page.getByRole('button', { name: 'Réessayer' })
    await expect(retryButton).toBeVisible({ timeout: 10000 })
    await expect(page.getByText('Le cockpit de gouvernance est indisponible')).toBeVisible()
    await retryButton.click()
    await expect(page.getByRole('heading', { name: 'Cockpit de gouvernance du président' })).toBeVisible()
  })

  test('secretary documents show recovery state and retry after failure', async ({ page }) => {
    await seedLocale(page, 'fr', 'secretary_general')

    await page.addInitScript(() => {
      ;(window as any).__forceSecretaryDocumentsError = true
    })

    await page.route('**/api/v1/documents', async (route) => {
      const shouldFail = await page.evaluate(() => (window as any).__forceSecretaryDocumentsError === true)
      if (shouldFail) {
        await page.evaluate(() => {
          ;(window as any).__forceSecretaryDocumentsError = false
        })
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Service indisponible' }) })
        return
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })

    await page.goto('/secretary/documents')
    const retryButton = page.getByRole('button', { name: 'Réessayer' })
    await expect(retryButton).toBeVisible({ timeout: 10000 })
    await expect(page.getByText("L'espace documentaire du secrétariat est indisponible")).toBeVisible()
    await retryButton.click()
    await expect(page.getByRole('heading', { name: 'Gouvernance documentaire officielle' })).toBeVisible()
  })

  test('secretary announcements show recovery state and retry after failure', async ({ page }) => {
    await seedLocale(page, 'fr', 'secretary_general')

    await page.addInitScript(() => {
      ;(window as any).__forceSecretaryAnnouncementsError = true
    })

    await page.route('**/api/v1/announcements/', async (route) => {
      const shouldFail = await page.evaluate(() => (window as any).__forceSecretaryAnnouncementsError === true)
      if (shouldFail) {
        await page.evaluate(() => {
          ;(window as any).__forceSecretaryAnnouncementsError = false
        })
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Service indisponible' }) })
        return
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })

    await page.goto('/secretary/announcements')
    const retryButton = page.getByRole('button', { name: 'Réessayer' })
    await expect(retryButton).toBeVisible({ timeout: 10000 })
    await expect(page.getByText("L'espace annonces est indisponible")).toBeVisible()
    await retryButton.click()
    await expect(page.getByRole('heading', { name: 'Annonces' })).toBeVisible()
  })

  test('secretary policies show recovery state and retry after failure', async ({ page }) => {
    await seedLocale(page, 'fr', 'secretary_general')

    await page.addInitScript(() => {
      ;(window as any).__forceSecretaryPoliciesError = true
    })

    await page.route('**/api/v1/policies/categories', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ categories: [] }),
      })
    })
    await page.route('**/api/v1/documents', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/policies', async (route) => {
      const shouldFail = await page.evaluate(() => (window as any).__forceSecretaryPoliciesError === true)
      if (shouldFail) {
        await page.evaluate(() => {
          ;(window as any).__forceSecretaryPoliciesError = false
        })
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Service indisponible' }) })
        return
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })

    await page.goto('/secretary/policies')
    const retryButton = page.getByRole('button', { name: 'Réessayer' })
    await expect(retryButton).toBeVisible({ timeout: 10000 })
    await expect(page.getByText("L'espace règles est indisponible")).toBeVisible()
    await retryButton.click()
    await expect(page.getByRole('heading', { name: 'Administration des règles' })).toBeVisible()
  })

  test('principal admin overview shows recovery state and retry after failure', async ({ page }) => {
    await seedLocale(page, 'fr', 'principal_admin')

    await page.addInitScript(() => {
      ;(window as any).__forceAdminOverviewError = true
    })

    await page.route('**/api/v1/documents', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/admin/audit/events**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/admin/ingestion-jobs/health', async (route) => {
      const shouldFail = await page.evaluate(() => (window as any).__forceAdminOverviewError === true)
      if (shouldFail) {
        await page.evaluate(() => {
          ;(window as any).__forceAdminOverviewError = false
        })
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Service indisponible' }) })
        return
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          queued_count: 0,
          processing_count: 0,
          failed_count: 0,
          completed_count: 0,
          retried_count: 0,
          recent_failures: [],
        }),
      })
    })
    await page.route('**/api/v1/memberships/', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/contributions/summary', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_expected: '0.00',
          total_paid: '0.00',
          total_balance: '0.00',
          total_count: 0,
        }),
      })
    })
    await page.route('**/api/v1/announcements/active', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/events/public', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/notifications/channels', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/tenants/*/settings', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tenant_id: 'tenant-demo-1',
          slug: 'demo',
          name: 'Combis Sport Verein',
          default_language: 'fr',
          branding: {
            primary_color: '#1f4f8f',
            logo_url: '',
          },
          modules: {
            membership: true,
            contributions: true,
            policies: true,
            disciplinary: true,
            events: true,
            announcements: true,
            chat: true,
            notifications: true,
          },
          operations: {
            last_backup_at: null,
            last_backup_status: 'completed',
            last_backup_reference: 'backup.tar.gz',
            last_restore_drill_at: null,
            last_restore_drill_status: 'passed',
            alert_posture: 'healthy',
            alert_contacts_configured: true,
            backup_retention_days: 30,
            notes: '',
            backup_is_stale: false,
            restore_drill_is_stale: false,
            alert_is_healthy: true,
            overall_status: 'healthy',
            status_message: 'Sauvegarde et reprise à jour.',
          },
          updated_at: '2026-07-16T00:00:00Z',
        }),
      })
    })

    await page.goto('/admin')
    const retryButton = page.getByRole('button', { name: 'Réessayer' })
    await expect(retryButton).toBeVisible({ timeout: 10000 })
    await expect(page.getByText("La vue d'ensemble admin est indisponible")).toBeVisible()
    await retryButton.click()
    await expect(page.getByRole('heading', { name: 'Vue d’ensemble administrateur principal' })).toBeVisible()
  })

  test('tenant operations show recovery state and retry after failure', async ({ page }) => {
    await seedLocale(page, 'fr', 'principal_admin')

    await page.addInitScript(() => {
      ;(window as any).__forceTenantOperationsError = true
    })

    await page.route('**/api/v1/tenants/*/settings', async (route) => {
      const shouldFail = await page.evaluate(() => (window as any).__forceTenantOperationsError === true)
      if (shouldFail) {
        await page.evaluate(() => {
          ;(window as any).__forceTenantOperationsError = false
        })
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Service indisponible' }) })
        return
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tenant_id: 'tenant-demo-1',
          slug: 'demo',
          name: 'Combis Sport Verein',
          default_language: 'fr',
          branding: {
            primary_color: '#1f4f8f',
            logo_url: '',
          },
          modules: {
            membership: true,
            contributions: true,
            policies: true,
            disciplinary: true,
            events: true,
            announcements: true,
            chat: true,
            notifications: true,
          },
          operations: {
            last_backup_at: null,
            last_backup_status: 'completed',
            last_backup_reference: 'backup.tar.gz',
            last_restore_drill_at: null,
            last_restore_drill_status: 'passed',
            alert_posture: 'healthy',
            alert_contacts_configured: true,
            backup_retention_days: 30,
            notes: '',
            backup_is_stale: false,
            restore_drill_is_stale: false,
            alert_is_healthy: true,
            overall_status: 'healthy',
            status_message: 'Sauvegarde et reprise à jour.',
          },
          updated_at: '2026-07-16T00:00:00Z',
        }),
      })
    })

    await page.goto('/admin/tenants')
    const retryButton = page.getByRole('button', { name: 'Réessayer' })
    await expect(retryButton).toBeVisible({ timeout: 10000 })
    await expect(page.getByText('Les opérations tenant sont indisponibles')).toBeVisible()
    await retryButton.click()
    await expect(page.getByRole('heading', { name: 'Command center' })).toBeVisible()
  })

  test('admin onboarding shows recovery state and retry after failure', async ({ page }) => {
    await seedLocale(page, 'fr', 'principal_admin')

    await page.addInitScript(() => {
      ;(window as any).__forceOnboardingError = true
    })

    await page.route('**/api/v1/documents', async (route) => {
      const shouldFail = await page.evaluate(() => (window as any).__forceOnboardingError === true)
      if (shouldFail) {
        await page.evaluate(() => {
          ;(window as any).__forceOnboardingError = false
        })
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Service indisponible' }) })
        return
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/announcements/active', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/events/public', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('**/api/v1/memberships/', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })

    await page.goto('/admin/onboarding')
    const retryButton = page.getByRole('button', { name: 'Réessayer' })
    await expect(retryButton).toBeVisible({ timeout: 10000 })
    await expect(page.getByText("L'assistant de démarrage est indisponible")).toBeVisible()
    await retryButton.click()
    await expect(page.getByRole('heading', { name: 'Assistant de démarrage' })).toBeVisible()
  })

  test('admin health center shows recovery state and retry after failure', async ({ page }) => {
    await seedLocale(page, 'fr', 'principal_admin')

    await page.addInitScript(() => {
      ;(window as any).__forceHealthCenterError = true
    })

    await page.route('**/api/v1/system/health', async (route) => {
      const shouldFail = await page.evaluate(() => (window as any).__forceHealthCenterError === true)
      if (shouldFail) {
        await page.evaluate(() => {
          ;(window as any).__forceHealthCenterError = false
        })
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Service indisponible' }) })
        return
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'healthy',
          version: '1.0.0',
          env: 'development',
          modules: ['membership', 'contributions', 'chat'],
          checks: {
            database: { status: 'ok', latency_ms: 12 },
            redis: { status: 'ok', latency_ms: 8 },
          },
        }),
      })
    })
    await page.route('**/api/v1/tenants/*/settings', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tenant_id: 'tenant-demo-1',
          slug: 'demo',
          name: 'Combis Sport Verein',
          default_language: 'fr',
          branding: {
            primary_color: '#1f4f8f',
            logo_url: '',
          },
          modules: {
            membership: true,
            contributions: true,
            policies: true,
            disciplinary: true,
            events: true,
            announcements: true,
            chat: true,
            notifications: true,
          },
          operations: {
            overall_status: 'healthy',
            status_message: 'Sauvegarde et reprise à jour.',
            last_backup_at: null,
            last_backup_status: 'completed',
            last_backup_reference: 'backup.tar.gz',
            last_restore_drill_at: null,
            last_restore_drill_status: 'passed',
            alert_posture: 'healthy',
            alert_contacts_configured: true,
            backup_retention_days: 30,
            notes: '',
          },
        }),
      })
    })

    await page.goto('/admin/health')
    const retryButton = page.getByRole('button', { name: 'Réessayer' })
    await expect(retryButton).toBeVisible({ timeout: 10000 })
    await expect(page.getByText('Le centre de santé est indisponible')).toBeVisible()
    await retryButton.click()
    await expect(page.getByRole('heading', { name: 'Preuves de reprise et état des dépendances' })).toBeVisible()
  })

  test('admin settings show recovery state and retry after failure', async ({ page }) => {
    await seedLocale(page, 'fr', 'principal_admin')

    await page.addInitScript(() => {
      ;(window as any).__forceSettingsError = true
    })

    await page.route('**/api/v1/tenants/*/settings', async (route) => {
      const shouldFail = await page.evaluate(() => (window as any).__forceSettingsError === true)
      if (shouldFail) {
        await page.evaluate(() => {
          ;(window as any).__forceSettingsError = false
        })
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Service indisponible' }) })
        return
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tenant_id: 'tenant-demo-1',
          slug: 'demo',
          name: 'Combis Sport Verein',
          default_language: 'fr',
          branding: {
            primary_color: '#1f4f8f',
            logo_url: '',
          },
          modules: {
            membership: true,
            contributions: true,
            policies: true,
            disciplinary: true,
            events: true,
            announcements: true,
            chat: true,
            notifications: true,
          },
          operations: {
            overall_status: 'healthy',
            status_message: 'Sauvegarde et reprise à jour.',
            last_backup_at: null,
            last_backup_status: 'completed',
            last_backup_reference: 'kairo-backup.tar.gz',
            last_restore_drill_at: null,
            last_restore_drill_status: 'passed',
            alert_posture: 'healthy',
            alert_contacts_configured: true,
            backup_retention_days: 30,
            notes: '',
          },
        }),
      })
    })
    await page.route('**/api/v1/admin/module-has-data**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: 'false' })
    })

    await page.goto('/admin/settings')
    const retryButton = page.getByRole('button', { name: 'Réessayer' })
    await expect(retryButton).toBeVisible({ timeout: 10000 })
    await expect(page.getByText('Les réglages du tenant sont indisponibles')).toBeVisible()
    await retryButton.click()
    await expect(page.getByRole('heading', { name: 'Réglages du tenant' })).toBeVisible()
  })

  test('admin settings stay French-first and do not expose unsupported locales', async ({ page }) => {
    await seedLocale(page, 'fr', 'principal_admin')
    await page.route('**/api/v1/tenants/*/settings', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tenant_id: 'tenant-demo-1',
          slug: 'demo',
          name: 'Combis Sport Verein',
          default_language: 'fr',
          branding: {
            primary_color: '#1f4f8f',
            logo_url: '',
          },
          modules: {
            membership: true,
            contributions: true,
            policies: true,
            disciplinary: true,
            events: true,
            announcements: true,
            chat: true,
            notifications: true,
          },
          operations: {
            overall_status: 'healthy',
            status_message: 'Sauvegarde et reprise à jour.',
            last_backup_at: null,
            last_backup_status: 'completed',
            last_backup_reference: 'kairo-backup.tar.gz',
            last_restore_drill_at: null,
            last_restore_drill_status: 'passed',
            alert_posture: 'healthy',
            alert_contacts_configured: true,
            backup_retention_days: 30,
            notes: '',
          },
        }),
      })
    })
    await page.route('**/api/v1/admin/module-has-data**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: 'false' })
    })

    await page.goto('/admin/settings')
    await expect(page.getByRole('heading', { name: 'Réglages du tenant' })).toBeVisible()
    await expect(page.getByText('Configurez le nom de votre organisation, son identité visuelle et les modules activés.')).toBeVisible()
    const settingsLanguageSelect = page
      .locator('.card-body')
      .filter({ has: page.getByText('Organisation') })
      .locator('select')
      .first()
    await expect(settingsLanguageSelect.locator('option[value="fr"]')).toHaveText('Français')
    await expect(settingsLanguageSelect.locator('option[value="en"]')).toHaveText('Anglais')
    await expect(settingsLanguageSelect.locator('option[value="de"]')).toHaveText('Allemand')
    await expect(settingsLanguageSelect.locator('option[value="nl"]')).toHaveCount(0)
  })

  test('admin documents render in French for principal admin', async ({ page }) => {
    await seedLocale(page, 'fr', 'principal_admin')
    await page.route('**/api/v1/documents', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      })
    })

    await page.goto('/admin/documents')
    await expect(page.getByRole('heading', { name: 'Réception documentaire' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Importer un document' })).toBeVisible()
    await expect(page.getByText('Aucun document pour le moment')).toBeVisible()
  })

  test('admin health center renders in French for principal admin', async ({ page }) => {
    await seedLocale(page, 'fr', 'principal_admin')
    await page.route('**/api/v1/system/health', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'healthy',
          version: '1.0.0',
          env: 'development',
          modules: ['membership', 'contributions', 'chat'],
          checks: {
            database: { status: 'ok', latency_ms: 12 },
            redis: { status: 'ok', latency_ms: 8 },
          },
        }),
      })
    })
    await page.route('**/api/v1/tenants/*/settings', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tenant_id: 'tenant-demo-1',
          slug: 'demo',
          name: 'Combis Sport Verein',
          default_language: 'fr',
          branding: {
            primary_color: '#1f4f8f',
            logo_url: '',
          },
          modules: {
            membership: true,
            contributions: true,
            policies: true,
            disciplinary: true,
            events: true,
            announcements: true,
            chat: true,
            notifications: true,
          },
          operations: {
            overall_status: 'healthy',
            status_message: 'Sauvegarde et reprise à jour.',
            last_backup_at: null,
            last_backup_status: 'completed',
            last_backup_reference: 'backup.tar.gz',
            last_restore_drill_at: null,
            last_restore_drill_status: 'passed',
            alert_posture: 'healthy',
            alert_contacts_configured: true,
            backup_retention_days: 30,
            notes: '',
          },
        }),
      })
    })

    await page.goto('/admin/health')
    await expect(page.getByRole('heading', { name: 'Preuves de reprise et état des dépendances' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Retour à la vue d’ensemble' })).toBeVisible()
    await expect(page.getByText('Sauvegarde, restauration et posture d’alerte')).toBeVisible()
  })

  test('admin notifications expose French simulation and full multi-channel live states', async ({ page }) => {
    await seedLocale(page, 'fr', 'principal_admin')
    let historyRows = [
      {
        id: 'notif-history-1',
        action: 'notification_dispatch',
        channel: 'email',
        recipient: 'ops@example.org',
        status: 'delivered',
        message: 'SMTP a confirmé la livraison finale.',
        delivered: true,
        simulation_only: false,
        delivery_stage: 'delivered',
        reconciliation_status: 'delivered',
        reconciliation_supported: true,
        provider_reference: 'smtp-ref-1',
        created_at: '2026-07-16T09:15:00Z',
      },
    ]
    const historyResponse = () => ({
      items: historyRows,
      summary: {
        total: historyRows.length,
        pending: historyRows.filter((entry) => entry.delivery_stage === 'accepted').length,
        delivered: historyRows.filter((entry) => entry.delivery_stage === 'delivered').length,
        failed: historyRows.filter((entry) => entry.delivery_stage === 'failed').length,
        simulated: historyRows.filter((entry) => entry.delivery_stage === 'simulated').length,
        stale_pending: 0,
      },
    })
    await page.route('**/api/v1/notifications/channels', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            channel: 'email',
            display_name: 'Email',
            description: 'Canal SMTP réel pour les notifications opérateur.',
            configured: true,
            simulation_only: false,
            target_hint: 'Adresse e-mail',
          },
          {
            channel: 'telegram',
            display_name: 'Telegram',
            description: 'Canal Telegram réel pour les notifications opérateur.',
            configured: true,
            simulation_only: false,
            target_hint: 'Identifiant Telegram ou @canal',
          },
          {
            channel: 'whatsapp',
            display_name: 'WhatsApp',
            description: 'Canal WhatsApp réel pour les notifications opérateur.',
            configured: true,
            simulation_only: false,
            target_hint: 'Numéro WhatsApp',
          },
        ]),
      })
    })
    await page.route('**/api/v1/notifications/history**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(historyResponse()),
      })
    })
    await page.route('**/api/v1/notifications/test', async (route) => {
      historyRows = [
        {
          id: 'notif-history-test-1',
          action: 'notification_test',
          channel: 'telegram',
          recipient: 'ops@example.org',
          status: 'simulated',
          message: 'Simulation Telegram acceptée.',
          delivered: false,
          simulation_only: true,
          delivery_stage: 'simulated',
          reconciliation_status: 'not_applicable',
          reconciliation_supported: false,
          provider_reference: null,
          created_at: '2026-07-16T10:00:00Z',
        },
        ...historyRows,
      ]
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          results: [
            {
              channel: 'telegram',
              status: 'simulated',
              message: 'Simulation Telegram acceptée.',
              delivered: false,
              simulation_only: true,
              delivery_stage: 'simulated',
              reconciliation_status: 'not_applicable',
              reconciliation_supported: false,
              provider_reference: null,
            },
          ],
        }),
      })
    })
    await page.route('**/api/v1/notifications/dispatch', async (route) => {
      const payload = route.request().postDataJSON()
      historyRows = [
        {
          id: `notif-history-${payload.channel}-1`,
          action: 'notification_dispatch',
          channel: payload.channel,
          recipient: 'ops@example.org',
          status: 'sent',
          message:
            payload.channel === 'telegram'
              ? 'Telegram a accepté la notification opérateur.'
              : payload.channel === 'whatsapp'
                ? 'WhatsApp a accepté la notification opérateur.'
                : 'SMTP a accepté la notification opérateur.',
          delivered: true,
          simulation_only: false,
          delivery_stage: 'accepted',
          reconciliation_status: 'pending',
          reconciliation_supported: true,
          provider_reference: `${payload.channel}-ref-1`,
          created_at: '2026-07-16T10:05:00Z',
        },
        ...historyRows,
      ]
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          channel: payload.channel,
          status: 'sent',
          message:
            payload.channel === 'telegram'
              ? 'Telegram a accepté la notification opérateur.'
              : payload.channel === 'whatsapp'
                ? 'WhatsApp a accepté la notification opérateur.'
              : 'SMTP a accepté la notification opérateur.',
          delivered: true,
          simulation_only: false,
          delivery_stage: 'accepted',
          reconciliation_status: 'pending',
          reconciliation_supported: true,
          provider_reference: `${payload.channel}-ref-1`,
        }),
      })
    })

    await page.goto('/admin/notifications')
    await expect(page.getByRole('heading', { name: 'Extensions de notification' })).toBeVisible()
    await expect(page.getByText('Capable en réel').first()).toBeVisible()
    await expect(page.getByText('Référence fournisseur: smtp-ref-1')).toBeVisible()
    await expect(page.getByText('Livrée').first()).toBeVisible()
    await page
      .locator('form')
      .filter({ has: page.getByRole('button', { name: 'Envoyer la notification réelle' }) })
      .locator('select')
      .selectOption('whatsapp')
    await page.getByRole('button', { name: 'Envoyer la notification réelle' }).click()
    await expect(page.getByText('La notification réelle a été acceptée pour le canal sélectionné.')).toBeVisible()
    await expect(page.getByText('WhatsApp a accepté la notification opérateur.')).toBeVisible()
    await expect(page.getByText('Référence fournisseur: whatsapp-ref-1')).toBeVisible()
  })

})
