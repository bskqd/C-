class NOTIFY {
  info = (component, text) => {
    return component.$notify({
      group: 'notify',
      title: component.$i18n.t('info') + '!',
      text: text,
      type: 'info'
    })
  }
  success = (component, text) => {
    return component.$notify({
      group: 'notify',
      title: component.$i18n.t('success') + '!',
      text: text,
      type: 'success'
    })
  }
  warning = (component, text) => {
    return component.$notify({
      group: 'notify',
      title: component.$i18n.t('warning') + '!',
      text: text,
      type: 'warn'
    })
  }
  danger = (component, text) => {
    return component.$notify({
      group: 'notify',
      title: component.$i18n.t('danger') + '!',
      text: text,
      type: 'error'
    })
  }
  error = (component, text) => {
    return component.$notify({
      group: 'notify',
      title: component.$i18n.t('error') + '!',
      text: text,
      type: 'error'
    })
  }
}

export const notify = new NOTIFY()
