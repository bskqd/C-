<template>
  <b-card header-tag="header">
    <b-table
      :items="items"
      :fields="fields"
      striped
      hover
    >
      <template #cell(institution)="row">
        {{ row.item.institution.name_ukr }}
      </template>
      <template #cell(ratio)="row">
        <vue-numeric
          v-model="row.item.ratio"
          @input="checkSumRatio(row)"
          :precision="2"
          :min="0"
          :max="100"
          currency="%"
          separator=","
          class="form-control" />
        <div v-if="row.item.error" class="mt-2 ml-5 position-absolute">
          <ValidationAlert :text="$t('ratingHigh')"/>
        </div>
      </template>

      <template #cell(consider)="row">
        <b-form-checkbox
          v-model="row.item.consider"
          @input="row.item.ratio = ''"
          :value="true"
          :unchecked-value="false"
          class="pt-0 pl-3"
        />
      </template>
    </b-table>
    <b-overlay
      :show="buttonLoader"
      spinner-variant="primary"
      opacity="0.65"
      blur="2px"
      variant="white"
      class="w-100 text-center"
      spinner-small
    >
      <b-button
        @click="setRatio"
        class="mt-1"
        type="button"
        variant="success"
      >
        {{ $t('save') }}
      </b-button>
    </b-overlay>
  </b-card>
</template>

<script src="./BackOfficeDealingEdit.js"/>

<style scoped>
  .form-control:disabled, .form-control[readonly] {
    background: #b7b7b736 !important;
  }
</style>
