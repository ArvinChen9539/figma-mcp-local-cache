<template>
  <div class="common-layout">
    <el-container class="main-container">
      <el-header class="app-header">
        <div class="header-content">
          <h2 class="logo-text">Figma MCP <span class="subtitle">Local Cache</span></h2>
        </div>
      </el-header>
      <el-main class="app-main">
        <el-card class="filter-card" shadow="hover">
          <div class="filter-bar">
            <el-input
              v-model="searchQuery"
              placeholder="搜索文件 Key / 节点 ID / 文件名称"
              class="search-input"
              clearable
              prefix-icon="Search"
              @clear="fetchData"
              @keyup.enter="fetchData"
            >
              <template #append>
                <el-button @click="fetchData">搜索</el-button>
              </template>
            </el-input>
            <el-date-picker
              v-model="dateRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="记录开始时间"
              end-placeholder="记录结束时间"
              class="date-picker"
              @change="fetchData"
            />
            <el-button type="primary" class="refresh-btn" @click="fetchData" icon="Refresh">刷新列表</el-button>
          </div>
        </el-card>

        <el-card class="table-card" shadow="never">
          <el-table :data="tableData" style="width: 100%" v-loading="loading" :header-cell-style="{ background: '#f8fafc', color: '#64748b' }">
            <el-table-column prop="id" label="ID" width="80" align="center" />
            <el-table-column prop="file_key" label="文件 Key" min_width="150">
              <template #default="scope">
                <el-tag size="small" type="info">{{ scope.row.file_key }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="name" label="文件名称" min_width="180">
              <template #default="scope">
                <span style="font-weight: 500; color: #1e293b">{{ scope.row.name || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="node_id" label="节点 ID" width="150">
              <template #default="scope">
                <el-tag v-if="scope.row.node_id" size="small" effect="plain">{{ scope.row.node_id }}</el-tag>
                <el-tag v-else size="small" type="success" effect="plain">整文件</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="depth" label="深度" width="100" align="center" />
            <el-table-column prop="last_modified" label="文件最后更新时间" width="200">
              <template #default="scope">
                <span class="date-text">{{ formatDate(scope.row.last_modified) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="updated_at" label="记录时间" width="180">
              <template #default="scope">
                <span class="date-text">{{ formatDate(scope.row.updated_at) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right" align="center">
              <template #default="scope">
                <el-button-group>
                  <el-button size="small" type="primary" plain @click="handleSync(scope.row)" :loading="syncLoading === scope.row.id" icon="RefreshRight">
                    同步
                  </el-button>
                  <el-button size="small" plain @click="handleDetail(scope.row)" icon="View">详情</el-button>
                  <el-popconfirm title="确定要删除这条缓存吗？" @confirm="handleDelete(scope.row)">
                    <template #reference>
                      <el-button size="small" type="danger" plain icon="Delete">删除</el-button>
                    </template>
                  </el-popconfirm>
                </el-button-group>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="total"
              @size-change="fetchData"
              @current-change="fetchData"
              background
            />
          </div>
        </el-card>

        <el-dialog v-model="detailVisible" title="缓存详情" width="60%" class="detail-dialog">
          <div v-if="detailLoading" class="loading-state">
            <el-icon class="is-loading"><Loading /></el-icon> 加载中...
          </div>
          <div v-else class="json-container">
            <pre class="json-view">{{ detailJson }}</pre>
          </div>
          <template #footer>
            <el-button @click="detailVisible = false">关闭</el-button>
          </template>
        </el-dialog>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getCacheList, deleteCache, syncCache, getCacheDetail } from '../api';
import { ElMessage } from 'element-plus';
import { Search, Refresh, RefreshRight, View, Delete, Loading } from '@element-plus/icons-vue';

const tableData = ref([]);
const loading = ref(false);
const syncLoading = ref(null);
const detailLoading = ref(false);
const detailVisible = ref(false);
const detailJson = ref('');
const searchQuery = ref('');
const dateRange = ref([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

const fetchData = async () => {
  loading.value = true;
  try {
    const res = await getCacheList({
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      search: searchQuery.value,
      created_from: dateRange.value && dateRange.value[0] ? dateRange.value[0].toISOString() : undefined,
      created_to: dateRange.value && dateRange.value[1] ? dateRange.value[1].toISOString() : undefined,
    });
    tableData.value = res.data.items;
    total.value = res.data.total;
  } catch (error) {
    ElMessage.error('获取数据失败');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const handleDetail = async (row) => {
  detailLoading.value = true;
  detailVisible.value = true;
  try {
    const res = await getCacheDetail(row.id);
    detailJson.value = JSON.stringify(res.data.data ?? res.data, null, 2);
  } catch (error) {
    ElMessage.error('获取详情失败');
    console.error(error);
  } finally {
    detailLoading.value = false;
  }
};

const handleSync = async (row) => {
  syncLoading.value = row.id;
  try {
    await syncCache(row.id);
    ElMessage.success('同步成功');
    fetchData();
  } catch (error) {
    ElMessage.error('同步失败: ' + (error.response?.data?.detail || error.message));
  } finally {
    syncLoading.value = null;
  }
};

const handleDelete = async (row) => {
  try {
    await deleteCache(row.id);
    ElMessage.success('删除成功');
    fetchData();
  } catch (error) {
    ElMessage.error('删除失败');
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString();
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.common-layout {
  min-height: 100vh;
  background-color: #f1f5f9;
}

.main-container {
  max-width: 1400px;
  margin: 0 auto;
}

.app-header {
  background-color: #fff;
  border-bottom: 1px solid #e2e8f0;
  height: 64px;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.header-content {
  width: 100%;
  padding: 0 20px;
}

.logo-text {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
}

.subtitle {
  color: #3b82f6;
  font-weight: 500;
}

.app-main {
  padding: 24px;
}

.filter-card {
  margin-bottom: 24px;
  border: none;
  border-radius: 12px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
}

.filter-bar {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  width: 360px;
}

.date-picker {
  width: 360px !important;
}

.table-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.date-text {
  color: #64748b;
  font-size: 13px;
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  padding: 0 12px 12px;
}

.json-container {
  background-color: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  max-height: 60vh;
  overflow: auto;
  border: 1px solid #e2e8f0;
}

.json-view {
  margin: 0;
  white-space: pre-wrap;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #334155;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  color: #64748b;
  gap: 8px;
}

:deep(.el-table__inner-wrapper::before) {
  display: none;
}
</style>
