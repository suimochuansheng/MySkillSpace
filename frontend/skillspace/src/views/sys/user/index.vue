<template>
  <div class="user-management">
    <el-card class="page-header">
      <div class="header-actions">
        <h2>用户管理</h2>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增用户
        </el-button>
      </div>
    </el-card>

    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="searchForm.email" placeholder="请输入邮箱" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户列表 -->
    <el-card class="table-card">
      <el-table :data="userList" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="phonenumber" label="手机号" />
        <el-table-column prop="roles" label="角色" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'">
              {{ row.is_active ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date_joined" label="创建时间" width="180" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="warning" size="small" @click="handleAssignRole(row)">分配角色</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchUserList"
        @current-change="fetchUserList"
      />
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle"
      width="600px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="formData.email" placeholder="请输入邮箱" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="手机号" prop="phonenumber">
          <el-input v-model="formData.phonenumber" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="formData.password" type="password" placeholder="请输入密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 角色分配对话框 -->
    <el-dialog 
      v-model="roleDialogVisible" 
      title="分配角色"
      width="500px"
      @open="handleRoleDialogOpen"
    >
      <el-form label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="currentUserName" disabled />
        </el-form-item>
        <el-form-item label="选择角色">
          <el-checkbox-group v-model="selectedRoleIds" v-loading="roleLoading">
            <el-checkbox 
              v-for="role in availableRoles" 
              :key="role.id" 
              :label="role.id"
              style="display: block; margin-bottom: 10px;"
            >
              {{ role.name }}
              <span style="color: #909399; font-size: 12px; margin-left: 8px;">({{ role.code }})</span>
            </el-checkbox>
          </el-checkbox-group>
          <div v-if="availableRoles.length === 0 && !roleLoading" style="color: #909399; padding: 20px 0;">
            暂无可用角色，请先在角色管理中创建角色
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRoleSubmit" :loading="roleSubmitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { userManagement, roleManagement } from '@/api/auth';

// 数据状态
const loading = ref(false);
const userList = ref([]);
const searchForm = reactive({
  username: '',
  email: ''
});

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
});

// 对话框状态
const dialogVisible = ref(false);
const dialogTitle = ref('新增用户');
const isEdit = ref(false);
const formRef = ref(null);
const formData = reactive({
  id: null,
  username: '',
  email: '',
  phonenumber: '',
  password: ''
});

const formRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
};

// 角色分配相关状态
const roleDialogVisible = ref(false);
const currentUserId = ref(null);
const currentUserName = ref('');
const availableRoles = ref([]);
const selectedRoleIds = ref([]);
const roleLoading = ref(false);
const roleSubmitting = ref(false);

// 获取用户列表
const fetchUserList = async () => {
  loading.value = true;
  try {
    const params = {
      ...searchForm,
      page: pagination.page,
      page_size: pagination.pageSize
    };
    const response = await userManagement.getList(params);
    
    // DRF标准分页格式处理
    if (response.results) {
      userList.value = response.results;
      pagination.total = response.count || 0;
    } else {
      // 兼容非分页格式
      userList.value = Array.isArray(response) ? response : [];
      pagination.total = userList.value.length;
    }
  } catch (error) {
    console.error('获取用户列表失败:', error);
    ElMessage.error(error.message || '获取用户列表失败');
    userList.value = [];
    pagination.total = 0;
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleSearch = () => {
  pagination.page = 1;
  fetchUserList();
};

// 重置
const handleReset = () => {
  searchForm.username = '';
  searchForm.email = '';
  handleSearch();
};

// 新增
const handleAdd = () => {
  isEdit.value = false;
  dialogTitle.value = '新增用户';
  Object.assign(formData, {
    id: null,
    username: '',
    email: '',
    phonenumber: '',
    password: ''
  });
  dialogVisible.value = true;
};

// 编辑
const handleEdit = (row) => {
  isEdit.value = true;
  dialogTitle.value = '编辑用户';
  Object.assign(formData, row);
  dialogVisible.value = true;
};

// 提交
const handleSubmit = async () => {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await userManagement.update(formData.id, formData);
          ElMessage.success('更新成功');
        } else {
          await userManagement.create(formData);
          ElMessage.success('创建成功');
        }
        dialogVisible.value = false;
        fetchUserList();
      } catch (error) {
        console.error('操作失败:', error);
        ElMessage.error(error.message || '操作失败');
      }
    }
  });
};

// 分配角色
const handleAssignRole = async (row) => {
  currentUserId.value = row.id;
  currentUserName.value = row.username || row.email;
  roleDialogVisible.value = true;
};

// 角色对话框打开时加载数据
const handleRoleDialogOpen = async () => {
  await fetchAvailableRoles();
  await fetchUserRoles();
};

// 获取所有可用角色
const fetchAvailableRoles = async () => {
  roleLoading.value = true;
  try {
    const response = await roleManagement.getList({ page_size: 1000 });
    // 处理分页数据
    if (response.results) {
      availableRoles.value = response.results;
    } else {
      availableRoles.value = Array.isArray(response) ? response : [];
    }
  } catch (error) {
    console.error('获取角色列表失败:', error);
    ElMessage.error(error.message || '获取角色列表失败');
    availableRoles.value = [];
  } finally {
    roleLoading.value = false;
  }
};

// 获取用户已分配的角色
const fetchUserRoles = async () => {
  try {
    // 直接使用用户详情接口
    const user = await userManagement.getList({ 
      page_size: 1000,
      page: 1
    }).then(response => {
      // 从列表中找到当前用户
      const results = response.results || response;
      return results.find(u => u.id === currentUserId.value);
    });
    
    // 使用后端返回的 role_ids 字段
    if (user && user.role_ids && Array.isArray(user.role_ids)) {
      selectedRoleIds.value = user.role_ids;
    } else {
      selectedRoleIds.value = [];
    }
  } catch (error) {
    console.error('获取用户角色失败:', error);
    selectedRoleIds.value = [];
  }
};

// 提交角色分配
const handleRoleSubmit = async () => {
  roleSubmitting.value = true;
  try {
    await userManagement.assignRoles(currentUserId.value, selectedRoleIds.value);
    ElMessage.success('角色分配成功');
    roleDialogVisible.value = false;
    // 刷新用户列表以显示最新角色
    await fetchUserList();
  } catch (error) {
    console.error('角色分配失败:', error);
    ElMessage.error(error.message || '角色分配失败');
  } finally {
    roleSubmitting.value = false;
  }
};

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该用户吗？', '提示', {
      type: 'warning'
    });
    await userManagement.delete(row.id);
    ElMessage.success('删除成功');
    fetchUserList();
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error);
      ElMessage.error(error.message || '删除失败');
    }
  }
};

onMounted(() => {
  fetchUserList();
});
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.el-pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
