<script setup>
import { ref, computed, onMounted } from 'vue'
import { get } from '@/api/index'
import { getRecommendations, toggleFavorite, getFavorites } from '@/api/listing'
import FilterSidebar from '@/components/FilterSidebar.vue'

const houses = ref([])
const currentPage = ref(1)
const totalPages = ref(1)
const total = ref(0)
const loading = ref(false)
const queryParams = ref({})
const recommended = ref([])
const favoriteIds = ref(new Set())
const sortBy = ref('default')

const sortedHouses = computed(() => {
  const list = [...houses.value]
  if (sortBy.value === 'price_asc') {
    list.sort((a, b) => parseFloat(a.unit_price) - parseFloat(b.unit_price))
  } else if (sortBy.value === 'price_desc') {
    list.sort((a, b) => parseFloat(b.unit_price) - parseFloat(a.unit_price))
  } else if (sortBy.value === 'size_asc') {
    list.sort((a, b) => parseFloat(a.house_size) - parseFloat(b.house_size))
  } else if (sortBy.value === 'size_desc') {
    list.sort((a, b) => parseFloat(b.house_size) - parseFloat(a.house_size))
  }
  return list
})

const fetchHouses = async () => {
  loading.value = true
  try {
    const params = { page: currentPage.value, ...queryParams.value }
    const res = await get('/listings/houses/', params)
    houses.value = res.data.houses
    totalPages.value = res.data.pages
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

const fetchRecommended = async () => {
  try {
    const res = await getRecommendations()
    recommended.value = res.data || []
  } catch {
    recommended.value = []
  }
}

const fetchFavorites = async () => {
  try {
    const res = await getFavorites()
    favoriteIds.value = new Set(res.data.map(h => h.id))
  } catch {
    favoriteIds.value = new Set()
  }
}

const handleToggleFavorite = async (houseId) => {
  try {
    await toggleFavorite(houseId)
    await fetchFavorites()
  } catch {
    // ignore
  }
}

const onSearch = (params) => {
  queryParams.value = params
  currentPage.value = 1
  fetchHouses()
}

const goPage = (p) => {
  if (p < 1 || p > totalPages.value) return
  currentPage.value = p
  fetchHouses()
}

onMounted(() => {
  fetchHouses()
  fetchRecommended()
  fetchFavorites()
})
</script>

<template>
  <div class="home-layout">
    <FilterSidebar @search="onSearch" />
    <main class="main-content">

      <div v-if="recommended.length" class="recommend-section">
        <h3 class="recommend-title">🔥 为你推荐</h3>
        <div class="recommend-grid">
          <div v-for="h in recommended" :key="'rec-' + h.id" class="recommend-card">
            <span class="recommend-tag">推荐</span>
            <div class="rec-card-img">
              <img :src="h.house_image || '/placeholder.jpg'" alt="house" />
            </div>
            <div class="rec-card-body">
              <h4>{{ h.house_name }}</h4>
              <p class="rec-meta">{{ h.house_type }} | {{ h.house_size }}㎡ | {{ h.house_position }}</p>
              <div class="rec-price">
                <span class="total">{{ h.total_price }}万</span>
                <span class="unit">{{ h.unit_price }}元/㎡</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="toolbar">
        <span class="result-bar" v-if="total">共 {{ total }} 套房源</span>
        <select v-model="sortBy" class="sort-select">
          <option value="default">默认排序</option>
          <option value="price_asc">价格从低到高</option>
          <option value="price_desc">价格从高到低</option>
          <option value="size_asc">面积从小到大</option>
          <option value="size_desc">面积从大到小</option>
        </select>
      </div>

      <div v-if="loading" class="loading">加载中...</div>

      <div v-else-if="houses.length === 0" class="empty">暂无符合条件的房源</div>

      <div v-else class="house-grid">
        <div v-for="h in sortedHouses" :key="h.id" class="house-card">
          <div class="card-img">
            <img :src="h.house_image || '/placeholder.jpg'" alt="house" />
            <button class="fav-btn" :class="{ active: favoriteIds.has(h.id) }" @click="handleToggleFavorite(h.id)">
              {{ favoriteIds.has(h.id) ? '❤' : '🤍' }}
            </button>
          </div>
          <div class="card-body">
            <h3>{{ h.house_name }}</h3>
            <p class="desc">{{ h.house_description?.slice(0, 50) }}...</p>
            <p class="meta">{{ h.house_type }} | {{ h.house_size }}㎡ | {{ h.house_position }}</p>
            <p class="addr">{{ h.city }} {{ h.house_address }}</p>
            <div class="price">
              <span class="total">{{ h.total_price }}万</span>
              <span class="unit">{{ h.unit_price }}元/㎡</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="totalPages > 1" class="pagination">
        <button :disabled="currentPage <= 1" @click="goPage(currentPage - 1)">上一页</button>
        <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
        <button :disabled="currentPage >= totalPages" @click="goPage(currentPage + 1)">下一页</button>
      </div>
    </main>
  </div>
</template>

<style scoped>
.home-layout { display: flex; gap: 24px; max-width: 1400px; margin: 24px auto; padding: 0 24px; align-items: flex-start; }
.main-content { flex: 1; min-width: 0; }

/* 推荐区域 */
.recommend-section { margin-bottom: 32px; }
.recommend-title { font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 16px; }
.recommend-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.recommend-card { border-radius: 10px; overflow: hidden; background: #fff; box-shadow: 0 2px 12px rgba(64,158,255,0.12); border: 1px solid #e6f1ff; position: relative; transition: transform 0.2s; }
.recommend-card:hover { transform: translateY(-3px); }
.recommend-tag { position: absolute; top: 10px; left: 10px; background: linear-gradient(135deg, #f56c6c, #e05050); color: #fff; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 4px; z-index: 2; }
.rec-card-img { height: 160px; overflow: hidden; background: #f0f2f5; }
.rec-card-img img { width: 100%; height: 100%; object-fit: cover; }
.rec-card-body { padding: 14px; }
.rec-card-body h4 { margin: 0 0 6px; font-size: 15px; font-weight: 600; color: #303133; }
.rec-meta { color: #909399; font-size: 12px; margin: 0 0 10px; }
.rec-price { display: flex; justify-content: space-between; align-items: center; }

/* 结果统计与排序 */
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.result-bar { font-size: 14px; color: #909399; }
.sort-select { padding: 6px 12px; border: 1px solid #dcdfe6; border-radius: 6px; font-size: 13px; color: #606266; outline: none; cursor: pointer; background: #fff; }
.sort-select:focus { border-color: #409eff; }
.loading, .empty { text-align: center; padding: 80px 0; font-size: 15px; color: #c0c4cc; }

/* 房源网格 */
.house-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.house-card { border-radius: 10px; overflow: hidden; background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.06); transition: transform 0.2s, box-shadow 0.2s; }
.house-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
.card-img { height: 200px; overflow: hidden; background: #f0f2f5; position: relative; }
.card-img img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
.house-card:hover .card-img img { transform: scale(1.05); }
.fav-btn { position: absolute; top: 10px; right: 10px; background: rgba(255,255,255,0.9); border: none; border-radius: 50%; width: 36px; height: 36px; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
.fav-btn:hover { transform: scale(1.15); }
.fav-btn.active { background: rgba(245,108,108,0.12); }
.card-body { padding: 16px; }
.card-body h3 { margin: 0 0 6px; font-size: 16px; font-weight: 600; color: #303133; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.desc { color: #909399; font-size: 12px; margin: 0 0 8px; line-height: 1.5; }
.meta { color: #606266; font-size: 12px; margin: 0 0 4px; }
.addr { color: #909399; font-size: 12px; margin: 0 0 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.price { display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid #f0f2f5; }
.total { font-size: 22px; font-weight: 700; color: #f56c6c; }
.unit { font-size: 12px; color: #909399; }

/* 分页 */
.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 32px; padding: 24px 0; }
.pagination button { padding: 8px 20px; cursor: pointer; border: 1px solid #dcdfe6; background: #fff; border-radius: 6px; font-size: 14px; color: #606266; transition: all 0.2s; }
.pagination button:disabled { cursor: not-allowed; opacity: 0.4; }
.pagination button:hover:not(:disabled) { border-color: #409eff; color: #409eff; }
.pagination span { font-size: 14px; color: #909399; }
</style>
