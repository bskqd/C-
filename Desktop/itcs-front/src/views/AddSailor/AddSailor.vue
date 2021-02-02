<template>
  <div>
    <div class="vx-card">
      <div class="card-header card-title pt-3 ml-2 mr-22">
        <h4 class="text-center">
          {{ $t('addNewSailor') }}
        </h4>
      </div>
      <div class="pageList">
        <b-form
          @submit.prevent="validateForm"
          class="w-full pageList"
        >
          <h5 class="text-bold-600 col-12 mb-1 mt-1">
            {{ $t('mainInfo') }}:
          </h5>
          <div class="mb-0">
            <b>
              {{ $t('nameUK') }}
              <span class="required-field-star">*</span>
            </b>
          </div>
          <div class="w-33">
            <b-form-input
              v-model="lastNameUK"
              @blur="$v.lastNameUK.$touch()"
              :placeholder="$t('lastName')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.lastNameUK.$dirty && !$v.lastNameUK.required)"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="($v.lastNameUK.$dirty && !$v.lastNameUK.maxLength)"
              :text="$t('tooLongField')"
            />
            <ValidationAlert
              v-else-if="$v.lastNameUK.$dirty && !$v.lastNameUK.alphaUA"
              :text="$t('noAlphaUA')"
            />
          </div>
          <div class="w-33">
            <b-form-input
              v-model="firstNameUK"
              @blur="$v.firstNameUK.$touch()"
              :placeholder="$t('name')"
              type="text"
            />
            <ValidationAlert
              v-if="$v.firstNameUK.$dirty && !$v.firstNameUK.required"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="$v.firstNameUK.$dirty && !$v.firstNameUK.maxLength"
              :text="$t('tooLongField')"
            />
            <ValidationAlert
              v-else-if="$v.firstNameUK.$dirty && !$v.firstNameUK.alphaUA"
              :text="$t('noAlphaUA')"
            />
          </div>
          <div class="w-33">
            <b-form-input
              v-model="middleNameUK"
              @blur="$v.middleNameUK.$touch()"
              :placeholder="$t('middleName')"
              type="text"
            />
            <ValidationAlert
              v-if="$v.middleNameUK.$dirty && !$v.middleNameUK.maxLength"
              :text="$t('tooLongField')"
            />
            <ValidationAlert
              v-else-if="$v.middleNameUK.$dirty && !$v.middleNameUK.alphaUA"
              :text="$t('noAlphaUA')"
            />
          </div>

          <div class="mb-0">
            <b>
              {{ $t('nameEN') }}
              <span class="required-field-star">*</span>
            </b>
          </div>
          <div class="w-33">
            <b-form-input
              v-model="lastNameEN"
              @blur="$v.lastNameEN.$touch()"
              :placeholder="$t('lastName')"
              type="text"
            />
            <ValidationAlert
              v-if="$v.lastNameEN.$dirty && !$v.lastNameEN.required"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="$v.lastNameEN.$dirty && !$v.lastNameEN.maxLength"
              :text="$t('tooLongField')"
            />
            <ValidationAlert
              v-else-if="$v.lastNameEN.$dirty && !$v.lastNameEN.alphaEN"
              :text="$t('noAlpha')"
            />
          </div>
          <div class="w-33">
            <b-form-input
              v-model="firstNameEN"
              @blur="$v.firstNameEN.$touch()"
              :placeholder="$t('name')"
              type="text"
            />
            <ValidationAlert
              v-if="$v.firstNameEN.$dirty && !$v.firstNameEN.required"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="$v.firstNameEN.$dirty && !$v.firstNameEN.maxLength"
              :text="$t('tooLongField')"
            />
            <ValidationAlert
              v-else-if="$v.firstNameEN.$dirty && !$v.firstNameEN.alphaEN"
              :text="$t('noAlpha')"
            />
          </div>
          <div class="w-50">
            <b>{{ $t('dateBorn') }}</b>
            <span class="required-field-star">*</span>
            <b-input-group>
              <b-form-input
                v-model="dateBorn"
                @blur="$v.dateBorn.$touch()"
                type="date"
              />
              <b-input-group-append>
                <b-form-datepicker
                  v-model="dateBorn"
                  @hidden="$v.dateBorn.$touch()"
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
              v-if="$v.dateBorn.$dirty && !$v.dateBorn.required"
              :text="$t('emptyField')"
            />
          </div>
          <div class="w-50">
            <SelectSex v-model="sex" ref="typesex"/>
            <ValidationAlert
              v-if="$v.sex.$dirty && !$v.sex.required"
              :text="$t('emptyField')"
            />
          </div>
          <div class="w-50">
            <b>
              {{ $t('taxNumber') }}
              <span
                v-if="!checkAccess('main-addSailorWithoutTaxNumber')"
                class="required-field-star"
              >
              *
            </span>
            </b>
            <b-form-input
              v-model="taxNumber"
              @blur="$v.taxNumber.$touch()"
              :placeholder="$t('taxNumber')"
              type="text"
            />
            <ValidationAlert
              v-if="$v.taxNumber.$dirty && !$v.taxNumber.required"
              :text="$t('emptyField')"
            />
          </div>
          <div class="w-50">
            <b>
              {{ $t('innPhoto') }}
            </b>
            <b-form-file
              v-model="innPhoto"
              @change="$v.innPhoto.$touch()"
              :placeholder="$t('innPhoto')"
              :browse-text="$t('browse')"
              accept="image/jpeg, image/png, image/jpg, application/pdf"
              multiple
            />
            <ValidationAlert
              v-if="$v.innPhoto.$dirty && $v.innPhoto.$invalid"
              :text="$t('maxSize')"
            />
          </div>
          <div>
            <b>
              {{ $t('sailorPhoto') }}
            </b>
            <b-form-file
              v-model="sailorPhoto"
              @change="$v.sailorPhoto.$touch()"
              :placeholder="$t('sailorPhoto')"
              :browse-text="$t('browse')"
              accept="image/jpeg, image/png, image/jpg"
              multiple
            />
            <ValidationAlert
              v-if="$v.sailorPhoto.$dirty && $v.sailorPhoto.$invalid"
              :text="$t('maxSize')"
            />
          </div>
          <div class="col-12 mb-1 text-center">
            <b-button
              class="mt-2"
              type="submit"
              variant="success"
            >
              {{ $t('save') }}
            </b-button>
          </div>
        </b-form>
      </div>
    </div>
  </div>
</template>

<script src="./AddSailor.js"/>

<style scoped>
.form-control.is-invalid {
  background-image: none
}
</style>
