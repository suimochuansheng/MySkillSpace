<template>
  <div class="menu-management">
    <el-card class="page-header">
      <div class="header-actions">
        <h2>菜单管理</h2>
        <el-button 
          type="primary" 
          @click="handleAdd"
          v-permission="'system:menu:add'"
        >
          <el-icon><Plus /></el-icon>
          新增菜单
        </el-button>
      </div>
    </el-card>

    <!-- 菜单树形表格 -->
    <el-card class="table-card">
      <el-table
        :data="menuList"
        border
        stripe
        row-key="id"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        v-loading="loading"
      >
        <el-table-column prop="name" label="菜单名称" width="200" />
        <el-table-column prop="icon" label="图标" width="100">
          <template #default="{ row }">
            <el-icon v-if="row.icon">
              <component :is="row.icon" />
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="menu_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.menu_type === 'M'" type="warning">目录</el-tag>
            <el-tag v-else-if="row.menu_type === 'C'" type="primary">菜单</el-tag>
            <el-tag v-else type="info">按钮</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路由地址" />
        <el-table-column prop="component" label="组件路径" />
        <el-table-column prop="perms" label="权限标识" />
        <el-table-column prop="order_num" label="排序" width="80" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleEdit(row)"
              v-permission="'system:menu:edit'"
            >编辑</el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="handleAdd(row)"
              v-permission="'system:menu:add'"
            >新增</el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(row)"
              v-permission="'system:menu:delete'"
            >删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle"
      width="700px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="上级菜单" prop="parent_id">
              <el-tree-select
                v-model="formData.parent_id"
                :data="menuTreeData"
                :props="{ value: 'id', label: 'name', children: 'children' }"
                placeholder="选择上级菜单"
                clearable
                check-strictly
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单类型" prop="menu_type">
              <el-radio-group v-model="formData.menu_type">
                <el-radio label="M">目录</el-radio>
                <el-radio label="C">菜单</el-radio>
                <el-radio label="F">按钮</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="菜单名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入菜单名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="显示排序" prop="order_num">
              <el-input-number v-model="formData.order_num" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20" v-if="formData.menu_type !== 'F'">
          <el-col :span="12">
            <el-form-item label="路由地址" prop="path">
              <el-input v-model="formData.path" placeholder="请输入路由地址" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单图标" prop="icon">
              <el-input v-model="formData.icon" placeholder="请输入图标名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20" v-if="formData.menu_type === 'C'">
          <el-col :span="24">
            <el-form-item label="组件路径" prop="component">
              <el-input v-model="formData.component" placeholder="请输入组件路径" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="权限标识" prop="perms">
              <el-input 
                v-model="formData.perms" 
                placeholder="如：system:user:list" 
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="备注" prop="remark">
              <el-input 
                v-model="formData.remark" 
                type="textarea" 
                :rows="2"
                placeholder="请输入备注信息"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { menuManagement } from '@/api/auth';

// 数据状态
const loading = ref(false);
const menuList = ref([]);

// 对话框状态
const dialogVisible = ref(false);
const dialogTitle = ref('新增菜单');
const isEdit = ref(false);
const formRef = ref(null);
const menuTreeData = ref([]);

const formData = reactive({
  id: null,
  parent_id: null,
  name: '',
  icon: '',
  menu_type: 'C',
  path: '',
  component: '',
  perms: '',
  order_num: 0,
  remark: ''
});

const formRules = {
  name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }],
  menu_type: [{ required: true, message: '请选择菜单类型', trigger: 'change' }],
  order_num: [{ required: true, message: '请输入显示排序', trigger: 'blur' }]
};

// 获取菜单列表
const fetchMenuList = async () => {
  loading.value = true;
  try {
    // 使用tree接口获取树形结构数据
    const response = await menuManagement.getTree();
    menuList.value = Array.isArray(response) ? response : [];
    
    // 构建树形选择器数据
    menuTreeData.value = buildTreeSelectData(menuList.value);
  } catch (error) {
    console.error('获取菜单列表失败:', error);
    ElMessage.error(error.message || '获取菜单列表失败');
    menuList.value = [];
  } finally {
    loading.value = false;
  }
};

// 构建树形选择器数据
const buildTreeSelectData = (menus) => {
  if (!Array.isArray(menus)) return [];
  
  const tree = menus.map(menu => {
    const node = {
      id: menu.id,
      name: menu.name,
      children: []
    };
    
    // 递归处理子菜单
    if (menu.children && Array.isArray(menu.children) && menu.children.length > 0) {
      node.children = buildTreeSelectData(menu.children);
    }
    
    return node;
  });
  
  return tree;
};

// 新增
const handleAdd = (row = null) => {
  isEdit.value = false;
  dialogTitle.value = row ? '新增子菜单' : '新增菜单';
  Object.assign(formData, {
    id: null,
    parent_id: row ? row.id : null,
    name: '',
    icon: '',
    menu_type: 'C',
    path: '',
    component: '',
    perms: '',
    order_num: 0,
    remark: ''
  });
  dialogVisible.value = true;
};

// 编辑
const handleEdit = (row) => {
  isEdit.value = true;
  dialogTitle.value = '编辑菜单';
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
          await menuManagement.update(formData.id, formData);
          ElMessage.success('更新成功');
        } else {
          await menuManagement.create(formData);
          ElMessage.success('创建成功');
        }
        dialogVisible.value = false;
        fetchMenuList();
      } catch (error) {
        console.error('操作失败:', error);
        ElMessage.error(error.message || '操作失败');
      }
    }
  });
};

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该菜单吗？删除后子菜单也会被删除！', '提示', {
      type: 'warning'
    });
    await menuManagement.delete(row.id);
    ElMessage.success('删除成功');
    fetchMenuList();
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error);
      ElMessage.error(error.message || '删除失败');
    }
  }
};

onMounted(() => {
  fetchMenuList();
});
</script>

<style scoped>
.menu-management {
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

.table-card {
  margin-bottom: 20px;
}
</style>
