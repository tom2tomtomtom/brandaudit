import { create } from 'zustand'

const useAuthStore = create((set) => ({
  user: null,
  role: null,
  login: (userData) => set({ user: userData, role: userData.role }),
  logout: () => set({ user: null, role: null }),
}))

export default useAuthStore
