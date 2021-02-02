<template>
  <b-card header-tag="header">
    <div class="d-flex wrap text-left">
      <div class="w-33">
        <label>
          {{ $t('registrationNumber') }}
          <span class="required-field-star">*</span>
        </label>
        <b-input
          v-model="registryNumber"
          @blur="$v.registryNumber.$touch()"
          :placeholder="$t('registrationNumber')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.registryNumber.$dirty && !$v.registryNumber.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-33">
        <label>
          {{ $t('serial') }}
          <span class="required-field-star">*</span>
        </label>
        <b-input
          v-model="serial"
          @blur="$v.serial.$touch()"
          :placeholder="$t('serial')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.serial.$dirty && !$v.serial.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-33">
        <label>
          {{ $t('number') }}
          <span class="required-field-star">*</span>
        </label>
        <b-input
          v-model="number"
          @blur="$v.number.$touch()"
          :placeholder="$t('number')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.number.$dirty && !$v.number.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.number.$dirty && !$v.number.maxLength"
          :text="$t('EducNumLength')"
        />
      </div>

      <div class="w-100 pl-1 pr-1 mt-1">
        <label>
          {{ $t('notes') }}
        </label>
        <b-input
          v-model="notes"
          :placeholder="$t('notes')"
          type="text"
        />
      </div>

      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        class="w-100 text-center mt-1"
        spinner-small
      >
        <b-button
          @click="checkInfo"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorEducationStatementTransfer.js" />
