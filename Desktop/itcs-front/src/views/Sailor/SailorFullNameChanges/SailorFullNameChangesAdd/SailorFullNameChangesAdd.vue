<template>
  <b-form @submit.prevent="checkFields">
    <div class="text-left">
      <div class="flex-row-sb form-group">
        <div class="col-4">
          <label>
            {{ $t('lastNameUK') }}
          </label>
          <b-input
            v-model="dataForm.lastNameUa"
            @blur="$v.dataForm.lastNameUa.$touch()"
            :placeholder="$t('lastNameUK')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataForm.lastNameUa.$dirty && !$v.dataForm.lastNameUa.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dataForm.lastNameUa.$dirty && !$v.dataForm.lastNameUa.alphaUA"
            :text="$t('noAlphaUA')"
          />
        </div>

        <div class="col-4">
          <label>
            {{ $t('firstNameUK') }}
          </label>
          <b-input
            v-model="dataForm.firstNameUa"
            @blur="$v.dataForm.firstNameUa.$touch()"
            :placeholder="$t('firstNameUK')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataForm.firstNameUa.$dirty && !$v.dataForm.firstNameUa.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dataForm.firstNameUa.$dirty && !$v.dataForm.firstNameUa.alphaUA"
            :text="$t('noAlphaUA')"
          />
        </div>

        <div class="col-4">
          <label>
            {{ $t('middleNameUK') }}
          </label>
          <b-input
            v-model="dataForm.middleNameUa"
            @blur="$v.dataForm.middleNameUa.$touch()"
            :placeholder="$t('middleNameUK')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataForm.middleNameUa.$dirty && !$v.dataForm.middleNameUa.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dataForm.middleNameUa.$dirty && !$v.dataForm.middleNameUa.alphaUA"
            :text="$t('noAlphaUA')"
          />
        </div>
      </div>

      <div class="flex-row-sb form-group">
        <div class="col-4">
          <label>
            {{ $t('lastNameEN') }}
          </label>
          <b-input
            v-model="dataForm.lastNameEn"
            @blur="$v.dataForm.lastNameEn.$touch()"
            :placeholder="$t('lastNameEN')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataForm.lastNameEn.$dirty && !$v.dataForm.lastNameEn.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dataForm.lastNameEn.$dirty && !$v.dataForm.lastNameEn.alphaEN"
            :text="$t('noAlpha')"
          />
        </div>

        <div class="col-4">
          <label>
            {{ $t('firstNameEN') }}
          </label>
          <b-input
            v-model="dataForm.firstNameEn"
            @blur="$v.dataForm.firstNameEn.$touch()"
            :placeholder="$t('firstNameEN')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataForm.firstNameEn.$dirty && !$v.dataForm.firstNameEn.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dataForm.firstNameEn.$dirty && !$v.dataForm.firstNameEn.alphaEN"
            :text="$t('noAlpha')"
          />
        </div>

        <div class="col-4">
          <label>
            {{ $t('middleNameEn') }}
          </label>
          <b-input
            v-model="dataForm.middleNameEn"
            @blur="$v.dataForm.middleNameEn.$touch()"
            :placeholder="$t('middleNameEn')"
            type="text"
          />
          <ValidationAlert
            v-if="$v.dataForm.middleNameEn.$dirty && !$v.dataForm.middleNameEn.alphaEN"
            :text="$t('noAlpha')"
          />
        </div>
      </div>

      <div class="col-6 form-group text-left mt-2">
        <label>
          {{ $t('dateModified') }}
          <span class="requared-field-star">*</span>
        </label>
        <b-input-group>
          <b-form-input
            v-model="dataForm.dateModified"
            @blur="$v.dataForm.dateModified.$touch()"
            type="date"
          />
          <b-input-group-append>
            <b-form-datepicker
              v-model="dataForm.dateModified"
              @hidden="$v.dataForm.dateModified.$touch()"
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
          v-if="$v.dataForm.dateModified.$dirty && !$v.dataForm.dateModified.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="col-12 form-group text-left mt-2">
        <FileDropZone ref="mediaContent" />
      </div>

      <div class="col-12 text-center mt-1">
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
            class="mt-1"
            type="submit"
            variant="success"
          >
            {{ $t('save') }}
          </b-button>
        </b-overlay>
      </div>
    </div>
  </b-form>
</template>

<script src="./SailorFullNameChangesAdd.js" />

<style scoped>

</style>
