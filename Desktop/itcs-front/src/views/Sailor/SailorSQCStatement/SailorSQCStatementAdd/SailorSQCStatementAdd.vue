<template>
  <b-form @submit.prevent="checkInfo">
    <div class="col-12 form-group text-left">
      <label>
        {{ $t('qualification') }} - {{ $t('rank') }}
        <span class="required-field-star">*</span>
      </label>
      <multiselect
        v-model="dataForm.newRank"
        @input="enterDoublePosition(dataForm.newRank, dataForm.newPosition)"
        @close="$v.dataForm.newRank.$touch()"
        :options="ranks"
        :label="labelName"
        :placeholder="$t('qualification') + ' - ' + $t('rank')"
        track-by="id"
      />
      <ValidationAlert
        v-if="$v.dataForm.newRank.$dirty && !$v.dataForm.newRank.required"
        :text="$t('emptyField')"
      />
    </div>

    <div class="col-12 form-group text-left mt-2">
      <label>
        {{ $t('position') }}
        <span class="required-field-star">*</span>
      </label>
      <multiselect
        v-model="dataForm.newPosition"
        @remove="removePosition"
        @close="$v.dataForm.newPosition.$touch()"
        :options="mappingSQCPositions(dataForm.newRank)"
        :label="labelName"
        :placeholder="$t('position')"
        :max="dataForm.newRank && dataForm.newRank.id === 22 ? 1 : 5"
        track-by="id"
        multiple
      >
        <span slot="noOptions">
          {{ $t('selectRank') }}
        </span>
        <span slot="maxElements">
          {{ $t('maxOptionsAmount') }}
        </span>
      </multiselect>
      <ValidationAlert
        v-if="$v.dataForm.newPosition.$dirty && !$v.dataForm.newPosition.required"
        :text="$t('emptyField')"
      />
    </div>

    <div class="col-12 form-group text-left mt-2">
      <FileDropZone ref="mediaContent" />
    </div>
    <b-overlay
      :show="buttonLoader"
      spinner-variant="primary"
      opacity="0.65"
      blur="2px"
      variant="white"
      class="w-100"
      spinner-small
    >
      <b-button
        type="submit"
        variant="success"
      >
        {{ $t('save') }}
      </b-button>
    </b-overlay>
  </b-form>
</template>

<script src="./SailorSQCStatementAdd.js" />

<style scoped>

</style>
