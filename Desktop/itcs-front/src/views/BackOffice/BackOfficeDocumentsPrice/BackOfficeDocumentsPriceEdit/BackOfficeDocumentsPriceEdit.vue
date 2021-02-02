<template>
  <b-card
    header-tag="header"
    class="pb-2"
  >
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase">
          {{ $t('editingPriceEti') }}
        </div>
        <unicon
          @click="hideDetailed(row)"
          name="multiply"
          fill="#42627e"
          height="20px"
          width="20px"
          class="close"
        />
      </div>
    </template>
    <div class="seafarerInfoList">
      <div class="w-50 mb-1">
        {{ $t('dateEffective') }}
        <b-input-group>
          <b-form-input
            v-model="dateStart"
            @blur="$v.dateStartObject.$touch"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="dateStart"
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

      <div class="w-50 mb-1">
        {{ $t('coming') }}
        <b-input
          v-model="coming"
          @blur="$v.coming.$touch"
          :placeholder="$t('coming')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.coming.$dirty && !$v.coming.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.coming.$dirty && !$v.coming.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-25 mb-1">
        {{ $t('toSQC') }}
        <b-input
          v-model="toSQC"
          @blur="$v.toSQC.$touch"
          :placeholder="$t('toSQC')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.toSQC.$dirty && !$v.toSQC.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.toSQC.$dirty && !$v.toSQC.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-25 mb-1">
        {{ $t('toQD') }}
        <b-input
          v-model="toQD"
          @blur="$v.toQD.$touch"
          :placeholder="$t('toQD')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.toQD.$dirty && !$v.toQD.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.toQD.$dirty && !$v.toQD.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-25 mb-1">
        {{ $t('toTD') }}
        <b-input
          v-model="toTD"
          @blur="$v.toTD.$touch"
          :placeholder="$t('toQD')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.toTD.$dirty && !$v.toTD.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.toTD.$dirty && !$v.toTD.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-25 mb-1">
        {{ $t('toSC') }}
        <b-input
          v-model="toSC"
          @blur="$v.toSC.$touch"
          :placeholder="$t('toSC')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.toSC.$dirty && !$v.toSC.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.toSC.$dirty && !$v.toSC.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-20 mb-1">
        {{ $t('toAgent') }}
        <b-input
          v-model="toAgent"
          @blur="$v.toAgent.$touch"
          :placeholder="$t('toAgent')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.toAgent.$dirty && !$v.toAgent.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.toAgent.$dirty && !$v.toAgent.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-20 mb-1">
        {{ $t('toCEC') }}
        <b-input
          v-model="toCEC"
          @blur="$v.toCEC.$touch"
          :placeholder="$t('toCEC')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.toCEC.$dirty && !$v.toCEC.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.toCEC.$dirty && !$v.toCEC.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-20 mb-1">
        {{ $t('toMedical') }}
        <b-input
          v-model="toMedical"
          @blur="$v.toMedical.$touch"
          :placeholder="$t('toMedical')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.toMedical.$dirty && !$v.toMedical.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.toMedical.$dirty && !$v.toMedical.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-20 mb-1">
        {{ $t('toMRC') }}
        <b-input
          v-model="toMRC"
          @blur="$v.toMRC.$touch"
          :placeholder="$t('toMRC')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.toMRC.$dirty && !$v.toMRC.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.toMRC.$dirty && !$v.toMRC.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-20 mb-1">
        {{ $t('toPortal') }}
        <b-input
          v-model="toPortal"
          @blur="$v.toPortal.$touch"
          :placeholder="$t('toPortal')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.toPortal.$dirty && !$v.toPortal.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.toPortal.$dirty && !$v.toPortal.minValue"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        class="w-100 text-center mt-3"
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

<script src="./BackOfficeDocumentsPriceEdit.js" />
