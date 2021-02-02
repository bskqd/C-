<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="w-33">
        <label>
          {{ $t('lastNameUK') }}
        </label>
        <b-input
          v-model="sailorDocument.last_name_ukr"
          @blur="$v.sailorDocument.last_name_ukr.$touch()"
          :placeholder="$t('lastNameUK')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.last_name_ukr.$dirty && !$v.sailorDocument.last_name_ukr.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.sailorDocument.last_name_ukr.$dirty && !$v.sailorDocument.last_name_ukr.alphaUA"
          :text="$t('noAlphaUA')"
        />
      </div>

      <div class="w-33">
        <label>
          {{ $t('firstNameUK') }}
        </label>
        <b-input
          v-model="sailorDocument.first_name_ukr"
          @blur="$v.sailorDocument.first_name_ukr.$touch()"
          :placeholder="$t('firstNameUK')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.first_name_ukr.$dirty && !$v.sailorDocument.first_name_ukr.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.sailorDocument.first_name_ukr.$dirty && !$v.sailorDocument.first_name_ukr.alphaUA"
          :text="$t('noAlphaUA')"
        />
      </div>

      <div class="w-33">
        <label>
          {{ $t('middleNameUK') }}
        </label>
        <b-input
          v-model="sailorDocument.middle_name_ukr"
          @blur="$v.sailorDocument.middle_name_ukr.$touch()"
          :placeholder="$t('middleNameUK')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.middle_name_ukr.$dirty && !$v.sailorDocument.middle_name_ukr.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.sailorDocument.middle_name_ukr.$dirty && !$v.sailorDocument.middle_name_ukr.alphaUA"
          :text="$t('noAlphaUA')"
        />
      </div>

      <div class="w-33">
        <label>
          {{ $t('lastNameEN') }}
        </label>
        <b-input
          v-model="sailorDocument.last_name_eng"
          @blur="$v.sailorDocument.last_name_eng.$touch()"
          :placeholder="$t('lastNameEN')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.last_name_eng.$dirty && !$v.sailorDocument.last_name_eng.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.sailorDocument.last_name_eng.$dirty && !$v.sailorDocument.last_name_eng.alphaEN"
          :text="$t('noAlpha')"
        />
      </div>

      <div class="w-33">
        <label>
          {{ $t('firstNameEN') }}
        </label>
        <b-input
          v-model="sailorDocument.first_name_eng"
          @blur="$v.sailorDocument.first_name_eng.$touch()"
          :placeholder="$t('firstNameEN')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.first_name_eng.$dirty && !$v.sailorDocument.first_name_eng.required"
          :text="$t('emptyField')"
        />
        <ValidationAlert
          v-else-if="$v.sailorDocument.first_name_eng.$dirty && !$v.sailorDocument.first_name_eng.alphaEN"
          :text="$t('noAlpha')"
        />
      </div>

      <div class="w-33">
        <label>
          {{ $t('middleNameEn') }}
        </label>
        <b-input
          v-model="sailorDocument.middle_name_eng"
          @blur="$v.sailorDocument.middle_name_eng.$touch()"
          :placeholder="$t('middleNameEn')"
          type="text"
        />
        <ValidationAlert
          v-if="$v.sailorDocument.middle_name_eng.$dirty && !$v.sailorDocument.middle_name_eng.alphaEN"
          :text="$t('noAlpha')"
        />
      </div>

      <div class="w-50">
        <label>
          {{ $t('dateModified') }}
          <span class="requared-field-star">*</span>
        </label>
        <b-input-group>
          <b-form-input
            v-model="sailorDocument.change_date"
            @blur="$v.sailorDocument.change_date.$touch()"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="sailorDocument.change_date"
              @hidden="$v.sailorDocument.change_date.$touch()"
              :locale="lang"
              :max="new Date()"
              min="1900-01-01"
              start-weekday="1"
              button-only
              right
            />
          </b-input-group-append>
        </b-input-group>
        <ValidationAlert
          v-if="$v.sailorDocument.change_date.$dirty && !$v.sailorDocument.change_date.required"
          :text="$t('emptyField')"
        />
      </div>

      <div>
        <FileDropZone ref="mediaContent" class="w-100 p-0" />
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
          @click="checkEditedRecord"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-card>
</template>

<script src="./SailorFullNameChangesEdit.js" />

<style scoped>

</style>
