<template>
  <b-card header-tag="header">
    <div class="d-flex wrap text-left">
      <div class="w-33 mb-1">
        {{ $t('typeDoc') }}
        <span class="requared-field-star">*</span>
        <multiselect
          v-model="dataForm.documentType"
          @close="$v.dataForm.documentType.$touch"
          :options="mappingAccrualTypeDoc"
          :placeholder="$t('typeDoc')"
          label="value"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.dataForm.documentType.$dirty && !$v.dataForm.documentType.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-33 mb-1">
        {{ $t('form') }}
        <span class="requared-field-star">*</span>
        <multiselect
          v-model="dataForm.formType"
          @close="$v.dataForm.formType.$touch"
          :options="formTypeList"
          :label="lang"
          :placeholder="$t('form')"
          track-by="id"
        />
        <ValidationAlert
          v-if="$v.dataForm.formType.$dirty && !$v.dataForm.formType.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-33 mb-1">
        {{ $t('dateEffective') }}
        <span class="requared-field-star">*</span>
        <b-input-group>
          <b-form-input
            v-model="dataForm.dateStart"
            @blur="$v.dateStartObject.$touch"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="dataForm.dateStart"
              @hidden="$v.dateStartObject.$touch()"
              :locale="lang"
              :min="dateTomorrow"
              max="2200-01-01"
              start-weekday="1"
              button-only
              required
              right
            />
          </b-input-group-append>
        </b-input-group>
        <ValidationAlert
          v-if="$v.dateStartObject.$dirty && !$v.dateStartObject.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dateStartObject.$dirty && (!$v.dateStartObject.maxValue || !$v.dateStartObject.minValue)"
          :text="$t('useTodayDate')"
        />
      </div>

      <div class="w-20 mb-1">
        {{ $t('coming') }}
        <span class="requared-field-star">*</span>
        <b-input
          v-model="dataForm.coming"
          @blur="$v.dataForm.coming.$touch"
          :placeholder="$t('coming')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.dataForm.coming.$dirty && !$v.dataForm.coming.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dataForm.coming.$dirty && !$v.dataForm.coming.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-20 mb-1">
        {{ $t('toSQC') }}
        <span class="requared-field-star">*</span>
        <b-input
          v-model="dataForm.toSQC"
          @blur="$v.dataForm.toSQC.$touch"
          :placeholder="$t('toSQC')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.dataForm.toSQC.$dirty && !$v.dataForm.toSQC.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dataForm.toSQC.$dirty && !$v.dataForm.toSQC.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-20 mb-1">
        {{ $t('toQD') }}
        <span class="requared-field-star">*</span>
        <b-input
          v-model="dataForm.toQD"
          @blur="$v.dataForm.toQD.$touch"
          :placeholder="$t('toQD')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.dataForm.toQD.$dirty && !$v.dataForm.toQD.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dataForm.toQD.$dirty && !$v.dataForm.toQD.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-20 mb-1">
        {{ $t('toTD') }}
        <span class="requared-field-star">*</span>
        <b-input
          v-model="dataForm.toTD"
          @blur="$v.dataForm.toTD.$touch"
          :placeholder="$t('toQD')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.dataForm.toTD.$dirty && !$v.dataForm.toTD.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dataForm.toTD.$dirty && !$v.dataForm.toTD.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-20 mb-1">
        {{ $t('toCEC') }}
        <span class="requared-field-star">*</span>
        <b-input
          v-model="dataForm.toCEC"
          @blur="$v.dataForm.toCEC.$touch"
          :placeholder="$t('toCEC')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.dataForm.toCEC.$dirty && !$v.dataForm.toCEC.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dataForm.toCEC.$dirty && !$v.dataForm.toCEC.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-20 mb-1">
        {{ $t('toSC') }}
        <span class="requared-field-star">*</span>
        <b-input
          v-model="dataForm.toSC"
          @blur="$v.dataForm.toSC.$touch"
          :placeholder="$t('toSC')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.dataForm.toSC.$dirty && !$v.dataForm.toSC.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dataForm.toSC.$dirty && !$v.dataForm.toSC.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-20 mb-1">
        {{ $t('toAgent') }}
        <span class="requared-field-star">*</span>
        <b-input
          v-model="dataForm.toAgent"
          @blur="$v.dataForm.toAgent.$touch"
          :placeholder="$t('toAgent')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.dataForm.toAgent.$dirty && !$v.dataForm.toAgent.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dataForm.toAgent.$dirty && !$v.dataForm.toAgent.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-20 mb-1">
        {{ $t('toMedical') }}
        <span class="requared-field-star">*</span>
        <b-input
          v-model="dataForm.toMedical"
          @blur="$v.dataForm.toMedical.$touch"
          :placeholder="$t('toMedical')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.dataForm.toMedical.$dirty && !$v.dataForm.toMedical.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dataForm.toMedical.$dirty && !$v.dataForm.toMedical.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-20 mb-1">
        {{ $t('toMRC') }}
        <span class="requared-field-star">*</span>
        <b-input
          v-model="dataForm.toMRC"
          @blur="$v.dataForm.toMRC.$touch"
          :placeholder="$t('toMRC')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.dataForm.toMRC.$dirty && !$v.dataForm.toMRC.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dataForm.toMRC.$dirty && !$v.dataForm.toMRC.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-20 mb-1">
        {{ $t('toPortal') }}
        <span class="requared-field-star">*</span>
        <b-input
          v-model="dataForm.toPortal"
          @blur="$v.dataForm.toPortal.$touch"
          :placeholder="$t('toPortal')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.dataForm.toPortal.$dirty && !$v.dataForm.toPortal.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dataForm.toPortal.$dirty && !$v.dataForm.toPortal.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

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
          @click="checkFields"
          class="mt-1"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>

  </b-card>
</template>

<script src="./BackOfficeDocumentsPriceAdd.js"></script>
