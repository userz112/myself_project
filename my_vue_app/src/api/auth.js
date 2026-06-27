import { get, post } from './index'

export const registerApi = (data) => post('/users/register/', data)

export const loginApi = (data) => post('/users/login/', data)

export const getUserInfoApi = () => get('/users/me/')
