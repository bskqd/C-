<template>
  <b-card header-tag="header">
    <div class="d-flex wrap text-left">
      <div class="w-40 mt-1">
        <label>
          {{ $t('nameUa') }}
          <span class="requared-field-star">*</span>
        </label>
        <b-form-input
          v-model="sailorDocument.name_ukr"
          @blur="$v.sailorDocument.name_ukr.$touch()"
          :placeholder="$t('nameUa')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.name_ukr.$dirty && !$v.sailorDocument.name_ukr.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.sailorDocument.name_ukr.$dirty && !$v.sailorDocument.name_ukr.alphaUA"
          :text="$t('noAlphaUA')"
        />
      </div>

      <div class="w-40 mt-1">
        <label>
          {{ $t('nameEn') }}
          <span class="requared-field-star">*</span>
        </label>
        <b-form-input
          v-model="sailorDocument.name_eng"
          @blur="$v.sailorDocument.name_eng.$touch()"
          :placeholder="$t('nameEn')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.name_eng.$dirty && !$v.sailorDocument.name_eng.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.sailorDocument.name_eng.$dirty && !$v.sailorDocument.name_eng.alphaEN"
          :text="$t('noAlpha')"
        />
      </div>

      <div class="w-20 mt-1">
        <label>
          {{ $t('abbreviation') }}
        </label>
        <b-form-input
          v-model="sailorDocument.name_abbr"
          @blur="$v.sailorDocument.name_abbr.$touch()"
          :placeholder="$t('abbreviation')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.name_abbr.$dirty && !$v.sailorDocument.name_abbr.maxLength"
          :text="$t('abbreviationMaxLength')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('contractNumber') }}
        </label>
        <b-form-input
          v-model="sailorDocument.contract_number"
          @blur="$v.sailorDocument.contract_number.$touch()"
          :placeholder="$t('contractNumber')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.contract_number.$dirty && !$v.sailorDocument.contract_number.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('contractDate') }}
        </label>
        <b-input-group>
          <b-form-input
            v-model="sailorDocument.contract_number_date"
            @blur="$v.contractDateObject.$touch()"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="sailorDocument.contract_number_date"
              @hidden="$v.contractDateObject.$touch()"
              :locale="lang"
              min="1900-01-01"
              max="2200-12-31"
              start-weekday="1"
              button-only
              right
            />
          </b-input-group-append>
        </b-input-group>
        <ValidationAlert
          v-if="$v.contractDateObject.$dirty && (!$v.contractDateObject.maxValue || !$v.contractDateObject.minValue)"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('directorName') }}
        </label>
        <b-form-input
          v-model="sailorDocument.director_name"
          @blur="$v.sailorDocument.director_name.$touch()"
          :placeholder="$t('directorName')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.director_name.$dirty && !$v.sailorDocument.director_name.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('position') }}
        </label>
        <b-form-input
          v-model="sailorDocument.director_position"
          @blur="$v.sailorDocument.director_position.$touch()"
          :placeholder="$t('position')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.director_position.$dirty && !$v.sailorDocument.director_position.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('accountantFullName') }}
        </label>
        <b-form-input
          v-model="sailorDocument.accountant_full_name"
          @blur="$v.sailorDocument.accountant_full_name.$touch()"
          :placeholder="$t('accountantFullName')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.accountant_full_name.$dirty && !$v.sailorDocument.accountant_full_name.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('requisites') }}
        </label>
        <b-form-input
          v-model="sailorDocument.requisites"
          @blur="$v.sailorDocument.requisites.$touch()"
          :placeholder="$t('requisites')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.requisites.$dirty && !$v.sailorDocument.requisites.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('bank') }}
        </label>
        <b-form-input
          v-model="sailorDocument.bank_name"
          @blur="$v.sailorDocument.bank_name.$touch()"
          :placeholder="$t('bank')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.bank_name.$dirty && !$v.sailorDocument.bank_name.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('checkNumber') }}
        </label>
        <b-form-input
          v-model="sailorDocument.check_number"
          @blur="$v.sailorDocument.check_number.$touch()"
          :placeholder="$t('checkNumber')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.check_number.$dirty && !$v.sailorDocument.check_number.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-33 mt-1">
        <label>
          {{ $t('edrpou') }}
          <span class="requared-field-star">*</span>
        </label>
        <b-form-input
          v-model="sailorDocument.okpo"
          @blur="$v.sailorDocument.okpo.$touch()"
          :placeholder="$t('edrpou')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.okpo.$dirty && !$v.sailorDocument.okpo.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.sailorDocument.okpo.$dirty && !$v.sailorDocument.okpo.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-33 mt-1">
        <label>
          {{ $t('vatNumber') }}
        </label>
        <b-form-input
          v-model="sailorDocument.nds_number"
          @blur="$v.sailorDocument.nds_number.$touch()"
          :placeholder="$t('vatNumber')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.nds_number.$dirty && !$v.sailorDocument.nds_number.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-33 mt-1">
        <label>
          {{ $t('mfoCode') }}
        </label>
        <b-form-input
          v-model="sailorDocument.mfo"
          @blur="$v.sailorDocument.mfo.$touch()"
          :placeholder="$t('mfoCode')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.mfo.$dirty && !$v.sailorDocument.mfo.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-100 mt-1">
        <label>
          {{ $t('address') }}
        </label>
        <b-form-input
          v-model="sailorDocument.address"
          @blur="$v.sailorDocument.address.$touch()"
          :placeholder="$t('street')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.address.$dirty && !$v.sailorDocument.address.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('email') }}
        </label>
        <b-form-input
          v-model="sailorDocument.email"
          @blur="$v.sailorDocument.email.$touch()"
          :placeholder="$t('email')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.email.$dirty && !$v.sailorDocument.email.email"
          :text="$t('invalidEmail')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('phoneNumber') }}
        </label>
        <phone-mask-input
          v-model="sailorDocument.phone"
          @onBlur="$v.sailorDocument.phone.$touch()"
          :placeholder="$t('phoneNumber')"
          class="w-full mainInfoPhone"
        />
        <small>
          {{ $t('phoneNumFormat') }}
        </small>
        <ValidationAlert
          v-if="$v.sailorDocument.phone.$dirty && (!$v.sailorDocument.phone.maxLength || !$v.sailorDocument.phone.minLength)"
          :text="$t('invalidPhoneNum')"
        />
      </div>

      <div class="w-100 pl-1">
        <b-form-checkbox
          v-model="sailorDocument.is_red"
          :value="true"
          :unchecked-value="false"
        >
          {{ $t('isRed') }}
        </b-form-checkbox>
      </div>

      <div class="w-100 pl-1">
        <b-form-checkbox
          v-model="sailorDocument.is_disable"
          :value="true"
          :unchecked-value="false"
        >
          {{ $t('isDisable') }}
        </b-form-checkbox>
      </div>

      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        class="w-100 d-flex justify-content-around mt-2"
        spinner-small
      >
        <b-button
          @click="checkFields()"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./BackOfficeETIListEdit.js" />
