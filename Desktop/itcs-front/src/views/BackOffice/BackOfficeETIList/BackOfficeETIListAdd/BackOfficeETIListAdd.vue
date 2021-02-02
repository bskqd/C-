<template>
  <div class="vx-card disable-rounded-right p-2">
    <div class="d-flex wrap text-left">
      <div class="w-40 mt-1">
        <label>
          {{ $t('nameUa') }}
          <span class="requared-field-star">*</span>
        </label>
        <b-form-input
          v-model="dataForm.nameUa"
          @blur="$v.dataForm.nameUa.$touch()"
          :placeholder="$t('nameUa')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataForm.nameUa.$dirty && !$v.dataForm.nameUa.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dataForm.nameUa.$dirty && !$v.dataForm.nameUa.alphaUA"
          :text="$t('noAlphaUA')"
        />
      </div>

      <div class="w-40 mt-1">
        <label>
          {{ $t('nameEn') }}
          <span class="requared-field-star">*</span>
        </label>
        <b-form-input
          v-model="dataForm.nameEn"
          @blur="$v.dataForm.nameEn.$touch()"
          :placeholder="$t('nameEn')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataForm.nameEn.$dirty && !$v.dataForm.nameEn.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dataForm.nameEn.$dirty && !$v.dataForm.nameEn.alphaEN"
          :text="$t('noAlpha')"
        />
      </div>

      <div class="w-20 mt-1">
        <label>
          {{ $t('abbreviation') }}
        </label>
        <b-form-input
          v-model="dataForm.nameAbbr"
          @blur="$v.dataForm.nameAbbr.$touch()"
          :placeholder="$t('abbreviation')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataForm.nameAbbr.$dirty && !$v.dataForm.nameAbbr.maxLength"
          :text="$t('abbreviationMaxLength')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('contractNumber') }}
        </label>
        <b-form-input
          v-model="dataForm.contractNumber"
          @blur="$v.dataForm.contractNumber.$touch()"
          :placeholder="$t('contractNumber')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataForm.contractNumber.$dirty && !$v.dataForm.contractNumber.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('contractDate') }}
        </label>
        <b-input-group>
          <b-form-input
            v-model="dataForm.contractDate"
            @blur="$v.contractDateObject.$touch()"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="dataForm.contractDate"
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
          v-model="dataForm.directorName"
          @blur="$v.dataForm.directorName.$touch()"
          :placeholder="$t('directorName')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataForm.directorName.$dirty && !$v.dataForm.directorName.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('position') }}
        </label>
        <b-form-input
          v-model="dataForm.directorPosition"
          @blur="$v.dataForm.directorPosition.$touch()"
          :placeholder="$t('position')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataForm.directorPosition.$dirty && !$v.dataForm.directorPosition.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('accountantFullName') }}
        </label>
        <b-form-input
          v-model="dataForm.accountantFullName"
          @blur="$v.dataForm.accountantFullName.$touch()"
          :placeholder="$t('accountantFullName')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataForm.accountantFullName.$dirty && !$v.dataForm.accountantFullName.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('requisites') }}
        </label>
        <b-form-input
          v-model="dataForm.requisites"
          @blur="$v.dataForm.requisites.$touch()"
          :placeholder="$t('requisites')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataForm.requisites.$dirty && !$v.dataForm.requisites.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('bank') }}
        </label>
        <b-form-input
          v-model="dataForm.bank"
          @blur="$v.dataForm.bank.$touch()"
          :placeholder="$t('bank')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataForm.bank.$dirty && !$v.dataForm.bank.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('checkNumber') }}
        </label>
        <b-form-input
          v-model="dataForm.checkNumber"
          @blur="$v.dataForm.checkNumber.$touch()"
          :placeholder="$t('checkNumber')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataForm.checkNumber.$dirty && !$v.dataForm.checkNumber.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-33 mt-1">
        <label>
          {{ $t('edrpou') }}
          <span class="requared-field-star">*</span>
        </label>
        <b-form-input
          v-model="dataForm.egprou"
          @blur="$v.dataForm.egprou.$touch()"
          :placeholder="$t('edrpou')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataForm.egprou.$dirty && !$v.dataForm.egprou.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.dataForm.egprou.$dirty && !$v.dataForm.egprou.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-33 mt-1">
        <label>
          {{ $t('vatNumber') }}
        </label>
        <b-form-input
          v-model="dataForm.ndsNumber"
          @blur="$v.dataForm.ndsNumber.$touch()"
          :placeholder="$t('vatNumber')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataForm.ndsNumber.$dirty && !$v.dataForm.ndsNumber.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-33 mt-1">
        <label>
          {{ $t('mfoCode') }}
        </label>
        <b-form-input
          v-model="dataForm.mfoCode"
          @blur="$v.dataForm.mfoCode.$touch()"
          :placeholder="$t('mfoCode')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataForm.mfoCode.$dirty && !$v.dataForm.mfoCode.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-100 pl-1 pr-1 mt-1">
        <label>
          {{ $t('address') }}
        </label>
        <b-form-input
          v-model="dataForm.address"
          @blur="$v.dataForm.address.$touch()"
          :placeholder="$t('street')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataForm.address.$dirty && !$v.dataForm.address.maxLength"
          :text="$t('invalidDataFormat')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('email') }}
        </label>
        <b-form-input
          v-model="dataForm.email"
          @blur="$v.dataForm.email.$touch()"
          :placeholder="$t('email')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.dataForm.email.$dirty && !$v.dataForm.email.email"
          :text="$t('invalidEmail')"
        />
      </div>

      <div class="w-50 mt-1">
        <label>
          {{ $t('phoneNumber') }}
        </label>
        <phone-mask-input
          v-model="dataForm.phone"
          @onBlur="$v.dataForm.phone.$touch()"
          :placeholder="$t('phoneNumber')"
          class="w-full mainInfoPhone"
        />
        <small>
          {{ $t('phoneNumFormat') }}
        </small>
        <ValidationAlert
          v-if="$v.dataForm.phone.$dirty && (!$v.dataForm.phone.maxLength || !$v.dataForm.phone.minLength)"
          :text="$t('invalidPhoneNum')"
        />
      </div>

      <div class="w-100 pl-1">
        <b-form-checkbox
          v-model="dataForm.isRed"
          :value="true"
          :unchecked-value="false"
        >
          {{ $t('isRed') }}
        </b-form-checkbox>
      </div>

      <div class="w-100 pl-1">
        <b-form-checkbox
          v-model="dataForm.isDisable"
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
  </div>
</template>

<script src="./BackOfficeETIListAdd.js" />
