import { ElMessageBox } from 'element-plus'

export function showStyledConfirm(message, title, options = {}) {
  return ElMessageBox.confirm(message, title, {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    customClass: 'sp-confirm-box',
    modalClass: 'sp-confirm-overlay',
    showClose: false,
    closeOnClickModal: false,
    closeOnPressEscape: true,
    autofocus: false,
    ...options
  })
}
