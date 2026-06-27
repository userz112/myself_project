import { get, post } from './index'

export const getRecommendations = () => get('/listings/recommendations/')

export const toggleFavorite = (house_id) => post('/listings/favorites/', { house_id })

export const getFavorites = () => get('/listings/favorites/')
