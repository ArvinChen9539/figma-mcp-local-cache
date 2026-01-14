<template>
  <div class="common-layout">
    <el-container>
      <el-header style="display: flex; align-items: center; border-bottom: 1px solid #eee;">
        <h2>Figma MCP 本地缓存管理</h2>
      </el-header>
      <el-main>
        <div style="margin-bottom: 20px; display: flex; gap: 10px; align-items: center;">
          <el-input
            v-model="searchQuery"
            placeholder="搜索文件 Key / 节点 ID / 文件名称"
            style="width: 320px"
            clearable
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
            style="width: 360px!important;flex-grow: 0;"
            @change="fetchData"
          />
          <el-button type="primary" @click="fetchData">刷新列表</el-button>
        </div>

        <el-table :data="tableData" style="width: 100%" v-loading="loading" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="file_key" label="文件 Key" min_width="150" />
          <el-table-column prop="name" label="文件名称" min_width="180" />
          <el-table-column prop="node_id" label="节点 ID" width="150">
            <template #default="scope">
              {{ scope.row.node_id || '整文件' }}
            </template>
          </el-table-column>
          <el-table-column prop="depth" label="深度" width="100" />
          <el-table-column prop="last_modified" label="文件最后更新时间" width="200">
            <template #default="scope">
              {{ formatDate(scope.row.last_modified) }}
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="记录时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.updated_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="scope">
              <el-button size="small" type="primary" @click="handleSync(scope.row)" :loading="syncLoading === scope.row.id">
                同步
              </el-button>
              <el-button size="small" @click="handleDetail(scope.row)">详情</el-button>
              <el-popconfirm title="确定要删除这条缓存吗？" @confirm="handleDelete(scope.row)">
                <template #reference>
                  <el-button size="small" type="danger">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>

        <div style="margin-top: 20px; display: flex; justify-content: flex-end;">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            @size-change="fetchData"
            @current-change="fetchData"
          />
        </div>
        <el-dialog v-model="detailVisible" title="缓存详情" width="60%">
          <div v-if="detailLoading">加载中...</div>
          <div v-else class="json-view">
            {{ detailJson }}
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
  try {
    const res = await getCacheDetail(row.id);
    detailJson.value = JSON.stringify(res.data.data ?? res.data, null, 2);
    detailVisible.value = true;
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
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleString();
};

onMounted(() => {
  fetchData();
});
</script>

<style>
.json-view {
  white-space: pre-wrap;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 12px;
  line-height: 1.5;
}
</style>
