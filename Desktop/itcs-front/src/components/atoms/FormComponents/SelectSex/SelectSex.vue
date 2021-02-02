<template>
  <div class="w-full">
    <b>
      {{ $t('sex') }}
      <span class="required-field-star">*</span>
    </b>
    <multiselect
      v-model="sex"
      @input="handleSelect"
      :searchable="true"
      :placeholder="$t('sex')"
      :options="mappingSex"
      :label="langSex"
      track-by="id"
    />
  </div>
</template>

<script src="./SelectSex.js"></script>

<style scoped></style>
