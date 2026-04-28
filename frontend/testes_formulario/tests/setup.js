import { vi } from 'vitest'
import { config } from '@vue/test-utils'

vi.mock('vue-router', () => ({
  useRoute: vi.fn(() => ({
    params: { produtorId: '1', fomentoId: '2' },
  })),
  useRouter: vi.fn(() => ({
    back: vi.fn(),
    push: vi.fn(),
  })),
}))

vi.mock('@/services/api', () => ({
  default: {
    get:  vi.fn(),
    post: vi.fn(),
  },
}))

config.global.stubs = {
  Loader2:     { template: '<span />' },
  FileText:    { template: '<span />' },
  UserPlus:    { template: '<span />' },
  Plus:        { template: '<span />' },
  X:           { template: '<span />' },
  Save:        { template: '<span />' },
  AlertCircle: { template: '<span />' },
  CheckCircle: { template: '<span />' },
  ArrowLeft:   { template: '<span />' },
}