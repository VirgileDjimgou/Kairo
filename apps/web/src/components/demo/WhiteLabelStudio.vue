<template>
  <section id="white-label-studio" class="studio card border-0 shadow-sm" data-testid="white-label-studio">
    <div class="card-body p-4">
      <div class="d-flex flex-wrap justify-content-between align-items-start gap-2 mb-1">
        <div>
          <h2 class="h5 fw-bold mb-1">{{ localeStore.t("demo.studioTitle") }}</h2>
          <p class="text-muted small mb-0">{{ localeStore.t("demo.studioSubtitle") }}</p>
        </div>
        <div class="btn-group btn-group-sm" role="group" :aria-label="localeStore.t('demo.studioPresets')">
          <button
            v-for="preset in presets"
            :key="preset.key"
            type="button"
            class="btn btn-outline-secondary"
            data-testid="studio-preset"
            @click="applyPreset(preset.key)"
          >
            {{ localeStore.t(preset.labelKey) }}
          </button>
        </div>
      </div>

      <div class="row g-4 mt-2">
        <div class="col-lg-7">
          <h3 class="h6 fw-semibold mb-3">{{ localeStore.t("demo.studioIdentity") }}</h3>
          <div class="row g-3">
            <div class="col-sm-6">
              <label class="form-label small fw-semibold text-muted" for="studio-display-name">
                {{ localeStore.t("demo.studioDisplayName") }}
              </label>
              <input id="studio-display-name" v-model="form.display_name" type="text" class="form-control" />
            </div>
            <div class="col-sm-6">
              <label class="form-label small fw-semibold text-muted" for="studio-short-name">
                {{ localeStore.t("demo.studioShortName") }}
              </label>
              <input id="studio-short-name" v-model="form.short_name" type="text" class="form-control" />
            </div>
            <div class="col-sm-6">
              <label class="form-label small fw-semibold text-muted" for="studio-logo">
                {{ localeStore.t("demo.studioLogoUrl") }}
              </label>
              <input id="studio-logo" v-model="form.logo_url" type="text" class="form-control" placeholder="/logo.svg" />
            </div>
            <div class="col-sm-6">
              <label class="form-label small fw-semibold text-muted" for="studio-favicon">
                {{ localeStore.t("demo.studioFaviconUrl") }}
              </label>
              <input id="studio-favicon" v-model="form.favicon_url" type="text" class="form-control" placeholder="/favicon.svg" />
            </div>
          </div>

          <h3 class="h6 fw-semibold mb-3 mt-4">{{ localeStore.t("demo.studioColors") }}</h3>
          <div class="row g-3">
            <div v-for="field in colorFields" :key="field.key" class="col-sm-6">
              <label class="form-label small fw-semibold text-muted" :for="`studio-${field.key}`">
                {{ localeStore.t(field.labelKey) }}
              </label>
              <div class="d-flex align-items-center gap-2">
                <input :id="`studio-${field.key}`" v-model="form[field.key]" type="color" class="form-control form-control-color w-auto" />
                <input v-model="form[field.key]" type="text" class="form-control" />
              </div>
            </div>
          </div>

          <h3 class="h6 fw-semibold mb-3 mt-4">{{ localeStore.t("demo.studioIcons") }}</h3>
          <div class="row g-3">
            <div class="col-sm-4">
              <label class="form-label small fw-semibold text-muted" for="studio-icon-192">
                {{ localeStore.t("demo.studioIcon192") }}
              </label>
              <input id="studio-icon-192" v-model="form.icon_192_url" type="text" class="form-control" placeholder="/pwa-192x192.png" />
            </div>
            <div class="col-sm-4">
              <label class="form-label small fw-semibold text-muted" for="studio-icon-512">
                {{ localeStore.t("demo.studioIcon512") }}
              </label>
              <input id="studio-icon-512" v-model="form.icon_512_url" type="text" class="form-control" placeholder="/pwa-512x512.png" />
            </div>
            <div class="col-sm-4">
              <label class="form-label small fw-semibold text-muted" for="studio-icon-maskable">
                {{ localeStore.t("demo.studioMaskable") }}
              </label>
              <input id="studio-icon-maskable" v-model="form.maskable_icon_url" type="text" class="form-control" placeholder="/pwa-512x512.png" />
            </div>
          </div>
          <p class="small text-muted mt-2 mb-0">{{ localeStore.t("demo.studioIconsHint") }}</p>
        </div>

        <div class="col-lg-5">
          <h3 class="h6 fw-semibold mb-3">{{ localeStore.t("demo.studioPreview") }}</h3>
          <div class="studio-preview p-3" :style="{ backgroundColor: form.background_color }">
            <div class="d-flex align-items-center gap-2 mb-3">
              <img v-if="previewLogo" :src="previewLogo" alt="" class="studio-preview__logo" />
              <span
                v-else
                class="studio-preview__mark"
                :style="{ backgroundColor: form.primary_color }"
                aria-hidden="true"
              >
                <i class="bi bi-diagram-3"></i>
              </span>
              <span>
                <strong class="d-block" :style="{ color: form.primary_color }">{{ form.display_name }}</strong>
                <small class="text-muted">{{ form.short_name }}</small>
              </span>
            </div>
            <div class="d-flex gap-2">
              <span class="studio-preview__swatch" :style="{ backgroundColor: form.primary_color }"></span>
              <span class="studio-preview__swatch" :style="{ backgroundColor: form.secondary_color }"></span>
              <span class="studio-preview__swatch" :style="{ backgroundColor: form.theme_color }"></span>
              <span class="studio-preview__swatch" :style="{ backgroundColor: form.background_color }"></span>
            </div>
          </div>

          <h3 class="h6 fw-semibold mb-2 mt-4">{{ localeStore.t("demo.studioInstallIcons") }}</h3>
          <div class="d-flex gap-3 align-items-end">
            <figure class="studio-icon m-0">
              <img :src="iconPreview(form.icon_192_url, '/pwa-192x192.png')" alt="192x192" width="64" height="64" />
              <figcaption class="small text-muted text-center mt-1">192</figcaption>
            </figure>
            <figure class="studio-icon m-0">
              <img :src="iconPreview(form.icon_512_url, '/pwa-512x512.png')" alt="512x512" width="80" height="80" />
              <figcaption class="small text-muted text-center mt-1">512</figcaption>
            </figure>
            <figure class="studio-icon studio-icon--maskable m-0">
              <img :src="iconPreview(form.maskable_icon_url || form.icon_512_url, '/pwa-512x512.png')" alt="maskable 512x512" width="80" height="80" />
              <figcaption class="small text-muted text-center mt-1">{{ localeStore.t("demo.studioMaskable") }}</figcaption>
            </figure>
          </div>

          <h3 class="h6 fw-semibold mb-2 mt-4">{{ localeStore.t("demo.studioInstallTitle") }}</h3>
          <p class="small text-muted mb-2">{{ localeStore.t(installHelpKey) }}</p>
          <p class="small text-muted mb-0">{{ localeStore.t("demo.studioNote") }}</p>

          <button type="button" class="btn btn-outline-secondary btn-sm mt-3" data-testid="studio-reset" @click="reset">
            <i class="bi bi-arrow-counterclockwise me-1"></i>{{ localeStore.t("demo.studioReset") }}
          </button>
        </div>
      </div>

      <h3 class="h6 fw-semibold mb-2 mt-4">{{ localeStore.t("demo.studioManifest") }}</h3>
      <pre class="studio-manifest mb-0" data-testid="studio-manifest">{{ manifestJson }}</pre>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, watch } from 'vue'
import { useLocaleStore } from '@/stores/locale.store'
import { useTenantStore } from '@/stores/tenant.store'
import { applyBranding, safeBrandingAsset } from '@/services/branding'
import { applyTenantManifest, installGuidanceKey } from '@/services/pwa-install'
import { KAIRO_BRANDING_DEFAULTS, type TenantBranding } from '@/api/branding.types'

const localeStore = useLocaleStore()
const tenantStore = useTenantStore()

const form = reactive<TenantBranding>({ ...KAIRO_BRANDING_DEFAULTS })

const colorFields = [
  { key: 'primary_color' as const, labelKey: 'demo.studioPrimaryColor' },
  { key: 'secondary_color' as const, labelKey: 'demo.studioSecondaryColor' },
  { key: 'theme_color' as const, labelKey: 'demo.studioThemeColor' },
  { key: 'background_color' as const, labelKey: 'demo.studioBackgroundColor' },
]

const presets = [
  { key: 'kairo', labelKey: 'demo.studioPresetKairo' },
  { key: 'sport', labelKey: 'demo.studioPresetSport' },
  { key: 'culture', labelKey: 'demo.studioPresetCulture' },
] as const

const PRESET_BRANDINGS: Record<string, Partial<TenantBranding>> = {
  kairo: {},
  sport: {
    display_name: 'Club Sportif Horizon',
    short_name: 'CS Horizon',
    primary_color: '#0a5c2e',
    secondary_color: '#c93146',
    background_color: '#f4f7f2',
    theme_color: '#0a5c2e',
    favicon_url: '/favicon.svg',
    notification_name: 'CS Horizon',
    support_name: 'CS Horizon',
    support_email: 'support@cs-horizon.example',
  },
  culture: {
    display_name: 'Association Culturelle Lumiere',
    short_name: 'AC Lumiere',
    primary_color: '#7a3ea1',
    secondary_color: '#e8a13a',
    background_color: '#faf7fd',
    theme_color: '#7a3ea1',
    favicon_url: '/favicon.svg',
    notification_name: 'AC Lumiere',
    support_name: 'AC Lumiere',
    support_email: 'contact@ac-lumiere.example',
  },
}

const installHelpKey = computed(() => installGuidanceKey())

function absoluteAsset(value: string, fallback: string): string {
  const safe = safeBrandingAsset(value, fallback)
  if (safe.startsWith('http://') || safe.startsWith('https://')) return safe
  return new URL(safe, window.location.origin).href
}

function buildPreviewManifest(): Record<string, unknown> {
  const iconSources = [
    { value: form.icon_192_url, fallback: '/pwa-192x192.png', sizes: '192x192', purpose: 'any' },
    { value: form.icon_512_url, fallback: '/pwa-512x512.png', sizes: '512x512', purpose: 'any' },
    {
      value: form.maskable_icon_url || form.icon_512_url,
      fallback: '/pwa-512x512.png',
      sizes: '512x512',
      purpose: 'maskable',
    },
  ]
  return {
    name: form.display_name,
    short_name: form.short_name,
    description: `${form.display_name} — association management`,
    lang: localeStore.currentLocale,
    theme_color: form.theme_color,
    background_color: form.background_color,
    display: 'standalone',
    orientation: 'any',
    start_url: '/dashboard',
    scope: '/',
    icons: iconSources.map((icon) => ({
      src: absoluteAsset(icon.value, icon.fallback),
      sizes: icon.sizes,
      type: 'image/png',
      purpose: icon.purpose,
    })),
  }
}

const manifestJson = computed(() => JSON.stringify(buildPreviewManifest(), null, 2))

const previewLogo = computed(() => (form.logo_url ? safeBrandingAsset(form.logo_url, '') : ''))

function iconPreview(value: string, fallback: string): string {
  return safeBrandingAsset(value, fallback)
}

let previewManifestUrl: string | null = null

function applyPreview(): void {
  applyBranding(form)
  const manifest = buildPreviewManifest()
  const link = document.querySelector<HTMLLinkElement>('link[rel="manifest"]')
  if (!link) return
  if (previewManifestUrl) URL.revokeObjectURL(previewManifestUrl)
  previewManifestUrl = URL.createObjectURL(
    new Blob([JSON.stringify(manifest)], { type: 'application/manifest+json' }),
  )
  link.href = previewManifestUrl
}

function restoreRealBranding(): void {
  if (previewManifestUrl) {
    URL.revokeObjectURL(previewManifestUrl)
    previewManifestUrl = null
  }
  const tenant = tenantStore.currentTenant
  applyBranding(tenant?.branding ?? null)
  applyTenantManifest(tenant?.slug ?? null)
}

function applyPreset(key: string): void {
  Object.assign(form, { ...KAIRO_BRANDING_DEFAULTS, ...(PRESET_BRANDINGS[key] ?? {}) })
}

function reset(): void {
  Object.assign(form, { ...KAIRO_BRANDING_DEFAULTS })
  restoreRealBranding()
}

watch(form, applyPreview, { deep: true })
onBeforeUnmount(restoreRealBranding)
</script>

<style scoped>
.studio {
  border-radius: 1rem;
}

.studio-preview {
  border-radius: 0.9rem;
  border: 1px solid #e2e8f0;
}

.studio-preview__logo {
  width: 2.25rem;
  height: 2.25rem;
  object-fit: contain;
}

.studio-preview__mark {
  display: inline-flex;
  width: 2.25rem;
  height: 2.25rem;
  align-items: center;
  justify-content: center;
  border-radius: 0.65rem;
  color: #fff;
}

.studio-preview__swatch {
  width: 1.6rem;
  height: 1.6rem;
  border-radius: 0.45rem;
  border: 1px solid rgba(15, 33, 56, 0.12);
}

.studio-icon img {
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  background: #fff;
  object-fit: contain;
}

.studio-icon--maskable img {
  border-radius: 50%;
  overflow: hidden;
}

.studio-manifest {
  max-height: 16rem;
  overflow: auto;
  padding: 0.75rem;
  border-radius: 0.75rem;
  background: #14233a;
  color: #eaf1fb;
  font-size: 0.75rem;
}
</style>
