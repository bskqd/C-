<template>
  <div
    v-if="prev || next || count || current"
    class="w-100 d-flex justify-content-sm-around"
  >
    <div class="w-50 d-flex justify-content-sb">
      <div v-if="count">
        {{ amountLabel ? $t(`${amountLabel}`) : $t('countDoc') }}: {{ count }}
      </div>
      <div v-if="current">
        {{ $t('numberPage')}}: {{ current }}
      </div>
    </div>
    <div class="w-50 text-right">
      <b-button
        v-if="prev"
        @click="changePage(prev)"
        class="font-large-1"
        variant="outline-secondary"
      >
        &larr;
      </b-button>
      <b-button
        v-if="next"
        @click="changePage(next)"
        class="font-large-1"
        variant="outline-secondary"
      >
        &rarr;
      </b-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Paginate',
  props: {
    current: Number,
    next: String,
    prev: String,
    count: Number,
    changePage: Function,
    amountLabel: String
  }
}
</script>
