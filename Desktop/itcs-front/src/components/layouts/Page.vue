<template>
  <div v-if="access" class="layout--main main-vertical navbar-sticky footer-static">
    <div class="vs-content-sidebar v-nav-menu items-no-padding" style="touch-action: none; user-select: none; -webkit-user-drag: none; -webkit-tap-highlight-color: rgba(0, 0, 0, 0);">
      <div class="vs-sidebar vs-sidebar-primary vs-sidebar-parent vs-sidebar-reduceNotRebound">
        <Menu :active="page"/>
      </div>
    </div>
    <div class="content-area-reduced" id="content-area">
      <div id="content-overlay"></div>
      <div class="relative">
          <TopBar :active="page" />
      </div>
      <div class="content-wrapper">
        <div class="router-view">
          <slot />
        </div>
      </div>
    </div>
  </div>
  <div
    v-else
    class="no-permission"
  >
    <div>{{ $t('noPermission') }}</div>
    <b-button @click="goBack">{{ $t('back') }}</b-button>
  </div>
</template>

<script>
import Menu from '@/components/molecules/Menu/Menu.vue'
import TopBar from '@/components/molecules/TopBar/TopBar.vue'
import { goBack } from '@/mixins/main'

export default {
  name: 'Page',
  props: {
    page: String,
    access: Boolean
  },
  components: {
    Menu,
    TopBar
  },
  data () {
    return {
      goBack
    }
  }
}
</script>
