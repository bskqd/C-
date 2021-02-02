<template>
  <b-tab
    @click="$router.push({name: link})"
    :active="pathname.includes(link.split('-')[0])"
  >
    <template slot="title">
      <unicon
        v-if="icon"
        :name="icon"
        fill="#42627e"
        height="50px"
        width="50px"/>
      <b-badge
        v-if="tabsCount && tabsCount[countDocKey]"
        pill
      >
        {{ tabsCount[countDocKey] }}
      </b-badge>
      <div class="text-uppercase">
        {{ $t(labelKey) }}
      </div>
    </template>
    <b-card-text>
      <b-tabs class="mainTabs" fill pills>
        <div :key="index" v-for="(tab, index) in tabs">
          <b-tab
            v-if="childPermissions[index]"
            :active="$route.name.includes(tab.link)"
          >
            <template slot="title">
              <router-link
                :to="{name: tab.link}"
                class="childTabLink"
              >
                <div class="flex-row-c">
                  <div class="text-uppercase">
                    {{ $t(tab.labelKey) }}
                  </div>
                  <div class="flex-row-c col-1">
                    <b-badge
                      v-if="tabsCount[tab.countDocKey]"
                      pill
                    >
                      {{ tabsCount[tab.countDocKey] }}
                    </b-badge>
                  </div>
                </div>
              </router-link>
            </template>
          </b-tab>
        </div>
      </b-tabs>
    </b-card-text>
  </b-tab>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'TabsList',
  props: {
    link: String,
    icon: String,
    countDocKey: String,
    labelKey: String,
    tabs: Array,
    childPermissions: Array
  },
  data () {
    return {
      pathname: window.location.pathname
    }
  },
  computed: {
    ...mapState({
      tabsCount: state => state.main.badgesCount
    })
  }
}
</script>

<style lang="sass">
  .mainTabs
    .nav-link
     padding: 0
    .childTabLink
      display: flex
      justify-content: center
      padding: 8px
</style>
