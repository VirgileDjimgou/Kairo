type ApiError = {
  response?: {
    data?: {
      detail?: string
    }
  }
}

export function getApiErrorDetail(error: unknown): string | null {
  const apiError = error as ApiError
  const detail = apiError.response?.data?.detail
  return typeof detail === 'string' && detail.trim().length > 0 ? detail : null
}

export function mapLoginError(detail: string | null): string {
  switch (detail) {
    case 'Invalid email or password':
      return 'Email or password is incorrect.'
    case 'Account is disabled':
      return 'This account is disabled. Contact an administrator for help.'
    case 'No active organization membership found':
    case 'You are not an active member of this organization':
      return 'You do not currently have active access to an organization.'
    default:
      return detail || 'Sign in failed. Please check your credentials and try again.'
  }
}

export function mapMfaError(detail: string | null): string {
  switch (detail) {
    case 'Invalid TOTP code':
      return 'The verification code is invalid. Try the current code from your authenticator app.'
    case 'Invalid or expired MFA token':
      return 'Your verification step expired. Sign in again to continue.'
    case 'No active organization membership found':
      return 'Your organization access is no longer active. Contact an administrator.'
    default:
      return detail || 'Invalid verification code.'
  }
}

export function mapAcceptInviteError(detail: string | null): string {
  switch (detail) {
    case 'Invalid invitation token':
      return 'This invitation link is invalid.'
    case 'Invitation has expired':
      return 'This invitation link has expired. Ask an administrator for a new one.'
    default:
      if (detail?.startsWith('Invitation is already ')) {
        return 'This invitation link is no longer valid. Ask an administrator for a fresh invitation if needed.'
      }
      return detail || 'Invitation acceptance failed. Please request a new link.'
  }
}

export function mapResetPasswordError(detail: string | null): string {
  switch (detail) {
    case 'Invalid reset token':
      return 'This reset link is invalid.'
    case 'Reset token has expired':
      return 'This reset link has expired. Request a new password reset email.'
    case 'Reset token has already been used':
      return 'This reset link has already been used. Request a new one to continue.'
    default:
      return detail || 'Password reset failed. Request a new link and try again.'
  }
}

export function mapForgotPasswordError(detail: string | null): string {
  return (
    detail ||
    'Password recovery is temporarily unavailable. Please try again in a moment.'
  )
}
