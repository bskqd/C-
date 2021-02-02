<template>
  <div v-if="location === 'topbar'"
    class="d-flex flex-row justify-content-between mt-1 itemList"
  >
    <span>{{ $t(labelKey) }}</span>
    <span>{{ notify }}</span>
    <router-link
      to="/statement-processing"
      replace
    >
      <component
        v-if="icon"
        :is="icon"
        size="1.5x"
      />
    </router-link>
  </div>
  <li
    v-else
    :class="{active: activePage, 'ml-2': child, 'mb-1': !child}"
    class="vs-sidebar--item"
  >
    <router-link :to="routingLink" replace>
      <span :class="{'feather-icon': child}">
        <component
          v-if="icon"
          :is="icon"
          size="1.5x"
        />
      </span>
      <span>
        {{ $t(labelKey) }}
      </span>
      <div
        v-if="notify"
        class="con-vs-chip ml-auto vs-chip-success con-color"
        style="color: rgba(255, 255, 255, 0.9);"
      >
        <span class="text-chip vs-chip--text">
          {{ notify }}
        </span>
      </div>
    </router-link>
  </li>
</template>

<script>
import { HomeIcon, CircleIcon, CheckCircleIcon, UploadIcon, PlusSquareIcon, BookIcon, DollarSignIcon,
  PercentIcon, ArrowRightCircleIcon, ArchiveIcon }
  from 'vue-feather-icons'

export default {
  name: 'ListItem',
  components: {
    HomeIcon,
    CircleIcon,
    CheckCircleIcon,
    UploadIcon,
    PlusSquareIcon,
    BookIcon,
    DollarSignIcon,
    PercentIcon,
    ArrowRightCircleIcon,
    ArchiveIcon
  },
  props: {
    activePage: [String, Boolean],
    labelKey: String,
    notify: [String, Number],
    icon: String,
    child: Boolean,
    routingLink: String,
    location: String
  }
}
</script>

<style scoped>
.itemList a {
  color: #42627e !important;
  width: 25px;
  height: 25px;
}
</style>
