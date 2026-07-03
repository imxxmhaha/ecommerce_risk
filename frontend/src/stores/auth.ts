import { reactive } from 'vue'
import { getMe, login as loginApi } from '../api/auth'

export const TOKEN_KEY = 'ecommerce_risk_token'

export interface AuthUser {
  id: number
  username: string
  real_name: string
  status: string
  roles: string[]
  permissions: string[]
}

export interface AuthMenu {
  menu_code: string
  menu_name: string
  route_path: string
  permission_code?: string
  icon?: string
  sort_order: number
}

interface LoginForm {
  username: string
  password: string
}

interface SessionPayload {
  token: string
  user: AuthUser
  permissions: string[]
  menus: AuthMenu[]
}

export const authStore = reactive({
  token: localStorage.getItem(TOKEN_KEY) || '',
  user: null as AuthUser | null,
  permissions: [] as string[],
  menus: [] as AuthMenu[],
  initialized: false,

  setSession(payload: SessionPayload) {
    this.token = payload.token
    this.user = payload.user
    this.permissions = payload.permissions || payload.user?.permissions || []
    this.menus = payload.menus || []
    this.initialized = true
    localStorage.setItem(TOKEN_KEY, payload.token)
  },

  async login(form: LoginForm) {
    const data = await loginApi(form)
    this.setSession(data)
    return data
  },

  async loadMe(force = false) {
    if (!this.token) return null
    if (this.initialized && !force) return this.user
    const data = await getMe()
    this.user = data.user
    this.permissions = data.permissions || []
    this.menus = data.menus || []
    this.initialized = true
    return this.user
  },

  hasPermission(permissionCode?: string) {
    return !permissionCode || this.permissions.includes(permissionCode)
  },

  firstMenuPath() {
    return this.menus[0]?.route_path || '/risk-check'
  },

  logout() {
    this.token = ''
    this.user = null
    this.permissions = []
    this.menus = []
    this.initialized = false
    localStorage.removeItem(TOKEN_KEY)
  }
})
