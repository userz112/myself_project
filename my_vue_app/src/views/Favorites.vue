<script setup>
import { ref, computed, onMounted } from 'vue'
import { getFavorites, toggleFavorite } from '@/api/listing'
import FilterSidebar from '@/components/FilterSidebar.vue'

const allHouses = ref([])
const loading = ref(false)
const filters = ref({})
const sortBy = ref('default')

const fetchFavorites = async () => {
  loading.value = true
  try {
    const res = await getFavorites()
    allHouses.value = res.data || []
  } finally {
    loading.value = false
  }
}

const filtered = computed(() => {
  let list = [...allHouses.value]

  const f = filters.value
  if (f.city) {
    list = list.filter(h => h.city.includes(f.city))
  }
  if (f.min_size) {
    list = list.filter(h => parseFloat(h.house_size) >= parseFloat(f.min_size))
  }
  if (f.max_size) {
    list = list.filter(h => parseFloat(h.house_size) <= parseFloat(f.max_size))
  }
  if (f.min_unit_price) {
    list = list.filter(h => parseFloat(h.unit_price) >= parseFloat(f.min_unit_price))
  }
  if (f.max_unit_price) {
    list = list.filter(h => parseFloat(h.unit_price) <= parseFloat(f.max_unit_price))
  }

  if (sortBy.value === 'size_asc') {
    list.sort((a, b) => parseFloat(a.house_size) - parseFloat(b.house_size))
  } else if (sortBy.value === 'size_desc') {
    list.sort((a, b) => parseFloat(b.house_size) - parseFloat(a.house_size))
  } else if (sortBy.value === 'price_asc') {
    list.sort((a, b) => parseFloat(a.unit_price) - parseFloat(b.unit_price))
  } else if (sortBy.value === 'price_desc') {
    list.sort((a, b) => parseFloat(b.unit_price) - parseFloat(a.unit_price))
  }

  return list
})

const onSearch = (params) => {
  filters.value = params
}

const handleToggle = async (houseId) => {
  try {
    await toggleFavorite(houseId)
    await fetchFavorites()
  } catch {}
}

onMounted(fetchFavorites)
</script>

<template>
  <div class="fav-layout">
    <FilterSidebar @search="onSearch" />
    <main class="main-content">
      <div class="toolbar">
        <span class="result-bar">我的收藏（共 {{ filtered.length }} 套）</span>
        <select v-model="sortBy" class="sort-select">
          <option value="default">默认排序</option>
          <option value="price_asc">价格从低到高</option>
          <option value="price_desc">价格从高到低</option>
          <option value="size_asc">面积从小到大</option>
          <option value="size_desc">面积从大到小</option>
        </select>
      </div>

      <div v-if="loading" class="loading">加载中...</div>

      <div v-else-if="filtered.length === 0" class="empty">暂无收藏房源</div>

      <div v-else class="house-grid">
        <div v-for="h in filtered" :key="h.id" class="house-card">
          <div class="card-img">
            <img :src="h.house_image || '/placeholder.jpg'" alt="house" />
            <button class="fav-btn active" @click="handleToggle(h.id)">❤</button>
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
    </main>
  </div>
</template>

<style scoped>
.fav-layout { display: flex; gap: 24px; max-width: 1400px; margin: 24px auto; padding: 0 24px; align-items: flex-start; }
.main-content { flex: 1; min-width: 0; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.result-bar { font-size: 14px; color: #909399; }
.sort-select { padding: 6px 12px; border: 1px solid #dcdfe6; border-radius: 6px; font-size: 13px; color: #606266; outline: none; cursor: pointer; background: #fff; }
.sort-select:focus { border-color: #409eff; }
.loading, .empty { text-align: center; padding: 80px 0; font-size: 15px; color: #c0c4cc; }
.house-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
.house-card { border-radius: 10px; overflow: hidden; background: #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.06); transition: transform 0.2s, box-shadow 0.2s; }
.house-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
.card-img { height: 200px; overflow: hidden; background: #f0f2f5; position: relative; }
.card-img img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
.house-card:hover .card-img img { transform: scale(1.05); }
.fav-btn { position: absolute; top: 10px; right: 10px; background: rgba(245,108,108,0.15); border: none; border-radius: 50%; width: 36px; height: 36px; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
.fav-btn:hover { transform: scale(1.15); }
.card-body { padding: 16px; }
.card-body h3 { margin: 0 0 6px; font-size: 16px; font-weight: 600; color: #303133; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.desc { color: #909399; font-size: 12px; margin: 0 0 8px; line-height: 1.5; }
.meta { color: #606266; font-size: 12px; margin: 0 0 4px; }
.addr { color: #909399; font-size: 12px; margin: 0 0 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.price { display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px solid #f0f2f5; }
.total { font-size: 22px; font-weight: 700; color: #f56c6c; }
.unit { font-size: 12px; color: #909399; }
</style>
