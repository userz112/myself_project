<script setup>
import { reactive } from 'vue'

const emit = defineEmits(['search'])

const areaPresets = [
  { label: '0-50㎡', min: 0, max: 50 },
  { label: '50-100㎡', min: 50, max: 100 },
  { label: '100-150㎡', min: 100, max: 150 },
  { label: '自定义', min: null, max: null, custom: true },
]

const pricePresets = [
  { label: '1000-5000', min: 1000, max: 5000 },
  { label: '5000-10000', min: 5000, max: 10000 },
  { label: '10000-15000', min: 10000, max: 15000 },
  { label: '15000-20000', min: 15000, max: 20000 },
  { label: '20000以上', min: 20000, max: null },
  { label: '自定义', min: null, max: null, custom: true },
]

const filters = reactive({
  city: '',
  areaPreset: null,
  areaMin: '',
  areaMax: '',
  pricePreset: null,
  priceMin: '',
  priceMax: '',
})

const selectAreaPreset = (item) => {
  filters.areaPreset = item.label
  if (item.custom) {
    filters.areaMin = ''
    filters.areaMax = ''
  } else {
    filters.areaMin = item.min
    filters.areaMax = item.max
  }
}

const selectPricePreset = (item) => {
  filters.pricePreset = item.label
  if (item.custom) {
    filters.priceMin = ''
    filters.priceMax = ''
  } else {
    filters.priceMin = item.min
    filters.priceMax = item.max
  }
}

const submit = () => {
  const params = {}
  if (filters.city) params.city = filters.city
  if (filters.areaMin !== '' && filters.areaMin !== null) params.min_size = filters.areaMin
  if (filters.areaMax !== '' && filters.areaMax !== null) params.max_size = filters.areaMax
  if (filters.priceMin !== '' && filters.priceMin !== null) params.min_unit_price = filters.priceMin
  if (filters.priceMax !== '' && filters.priceMax !== null) params.max_unit_price = filters.priceMax
  emit('search', params)
}

const reset = () => {
  filters.city = ''
  filters.areaPreset = null
  filters.areaMin = ''
  filters.areaMax = ''
  filters.pricePreset = null
  filters.priceMin = ''
  filters.priceMax = ''
  emit('search', {})
}
</script>

<template>
  <aside class="sidebar">
    <h3>筛选条件</h3>

    <div class="filter-group">
      <label>城市</label>
      <input v-model="filters.city" placeholder="输入城市名称" />
    </div>

    <div class="filter-group">
      <label>面积 (㎡)</label>
      <div class="preset-list">
        <button
          v-for="item in areaPresets"
          :key="item.label"
          :class="{ active: filters.areaPreset === item.label }"
          @click="selectAreaPreset(item)"
        >
          {{ item.label }}
        </button>
      </div>
      <div v-if="filters.areaPreset === '自定义'" class="custom-range">
        <input v-model="filters.areaMin" type="number" placeholder="最小" />
        <span>—</span>
        <input v-model="filters.areaMax" type="number" placeholder="最大" />
      </div>
    </div>

    <div class="filter-group">
      <label>单价 (元/㎡)</label>
      <div class="preset-list">
        <button
          v-for="item in pricePresets"
          :key="item.label"
          :class="{ active: filters.pricePreset === item.label }"
          @click="selectPricePreset(item)"
        >
          {{ item.label }}
        </button>
      </div>
      <div v-if="filters.pricePreset === '自定义'" class="custom-range">
        <input v-model="filters.priceMin" type="number" placeholder="最小" />
        <span>—</span>
        <input v-model="filters.priceMax" type="number" placeholder="最大" />
      </div>
    </div>

    <div class="sidebar-actions">
      <button class="btn-search" @click="submit">查询</button>
      <button class="btn-reset" @click="reset">重置</button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar { width: 250px; background: #fff; border-radius: 10px; padding: 24px 20px; flex-shrink: 0; align-self: flex-start; box-shadow: 0 1px 4px rgba(0,0,0,0.06); position: sticky; top: 84px; }
.sidebar h3 { margin: 0 0 20px; font-size: 16px; font-weight: 600; color: #303133; padding-bottom: 12px; border-bottom: 2px solid #409eff; }
.filter-group { margin-bottom: 22px; }
.filter-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 8px; color: #606266; }
.filter-group input[type="text"],
.filter-group input[type="number"] { width: 100%; padding: 8px 10px; border: 1px solid #dcdfe6; border-radius: 6px; font-size: 13px; outline: none; transition: border-color 0.2s; }
.filter-group input:focus { border-color: #409eff; box-shadow: 0 0 0 2px rgba(64,158,255,0.12); }
.preset-list { display: flex; flex-wrap: wrap; gap: 6px; }
.preset-list button { padding: 5px 12px; font-size: 12px; border: 1px solid #dcdfe6; border-radius: 6px; background: #fff; cursor: pointer; color: #606266; transition: all 0.2s; }
.preset-list button:hover { border-color: #409eff; color: #409eff; }
.preset-list button.active { background: #409eff; color: #fff; border-color: #409eff; }
.custom-range { display: flex; align-items: center; gap: 6px; margin-top: 8px; }
.custom-range input { width: 80px; padding: 6px 8px; border: 1px solid #dcdfe6; border-radius: 6px; font-size: 12px; outline: none; }
.custom-range input:focus { border-color: #409eff; }
.custom-range span { font-size: 13px; color: #909399; }
.sidebar-actions { display: flex; gap: 10px; margin-top: 28px; }
.btn-search { flex: 1; padding: 9px; background: #409eff; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; transition: background 0.2s; }
.btn-search:hover { background: #66b1ff; }
.btn-reset { flex: 1; padding: 9px; background: #fff; border: 1px solid #dcdfe6; border-radius: 6px; cursor: pointer; font-size: 14px; color: #606266; transition: all 0.2s; }
.btn-reset:hover { border-color: #409eff; color: #409eff; }
</style>
