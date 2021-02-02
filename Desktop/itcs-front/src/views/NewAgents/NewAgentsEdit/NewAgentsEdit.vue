<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="w-50">
        <label>
          {{ $t('serialAndNum') }}
          <span class="requared-field-star">*</span>
        </label>
        <b-form-input
          v-model="sailorDocument.serial_passport"
          @blur="$v.sailorDocument.serial_passport.$touch()"
          :placeholder="$t('serialAndNum')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.serial_passport.$dirty && !$v.sailorDocument.serial_passport.required"
          :text="$t('emptyField')"
        />
      </div>
      <div class="w-50">
        <label>
          {{ $t('taxNumber') }}
          <span class="requared-field-star">*</span>
        </label>
        <b-form-input
          v-model="sailorDocument.tax_number"
          @blur="$v.sailorDocument.tax_number.$touch()"
          :placeholder="$t('taxNumber')"
          type="number"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.tax_number.$dirty && !$v.sailorDocument.tax_number.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.sailorDocument.tax_number.$dirty && (!$v.sailorDocument.tax_number.minLength || !$v.sailorDocument.tax_number.maxLength)"
          :text="$t('invalidTaxNumLength')"
        />
      </div>
      <div class="w-33">
        <label>
          {{ $t('phoneNumber') }}
          <span class="requared-field-star">*</span>
        </label>
        <b-form-input
          v-model="phoneNumber"
          @blur="$v.phoneNumber.$touch()"
          :placeholder="$t('phoneNumber')"
        />
        <small>{{ $t('phoneNumFormat') }}</small>
        <ValidationAlert
          v-if="$v.phoneNumber.$dirty && !$v.phoneNumber.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.phoneNumber.$dirty && (!$v.phoneNumber.minLength || !$v.phoneNumber.maxLength ||
           !$v.phoneNumber.phoneNumber)"
          :text="$t('invalidPhoneNum')"
        />
      </div>
      <div class="w-33">
        <label>Telegram</label>
        <b-form-input
          v-model="telegram"
          @blur="$v.telegram.$touch()"
          placeholder="Telegram"
        />
        <small>{{ $t('phoneNumFormat') }}</small>
        <ValidationAlert
          v-if="$v.telegram.$dirty && (!$v.telegram.minLength || !$v.telegram.maxLength || !$v.telegram.phoneNumber)"
          :text="$t('invalidPhoneNum')"
        />
      </div>
      <div class="w-33">
        <label>Viber</label>
        <b-form-input
          v-model="viber"
          @blur="$v.viber.$touch()"
          placeholder="Viber"
        />
        <small>{{ $t('phoneNumFormat') }}</small>
        <ValidationAlert
          v-if="$v.viber.$dirty && (!$v.viber.minLength || !$v.viber.maxLength || !$v.viber.phoneNumber)"
          :text="$t('invalidPhoneNum')"
        />
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
          @click="validationCheck"
          class="mt-1"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./NewAgentsEdit.js" />
