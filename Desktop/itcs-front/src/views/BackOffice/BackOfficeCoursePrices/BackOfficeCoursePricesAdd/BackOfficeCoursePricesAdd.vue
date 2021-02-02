<template>
  <b-form @submit.prevent="checkCoursePrice">
    <div class="text-left">
      <div class="flex-row-sb form-group">
        <div class="col-6">
          <label>
            {{ $t('dateEffective') }}
            <span class="requared-field-star">*</span>
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateStart"
              @blur="$v.dateStartObject.$touch()"
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

        <div class="col-6">
          <label>
            {{ $t('course') }}
            <span class="requared-field-star">*</span>
          </label>
          <multiselect
            v-model="dataForm.course"
            :searchable="true"
            :placeholder="$t('course')"
            :options="mappingCourses"
            :label="labelName"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.course.$dirty && !$v.dataForm.course.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>

      <div class="flex-row-sb form-group">
        <div class="col-6">
          <label>
            {{ $t('price') }}
            <span class="requared-field-star">*</span>
          </label>
          <b-input
            v-model="dataForm.price"
            @blur="$v.dataForm.price.$touch()"
            :placeholder="$t('price')"
            type="number"
            step="0.01"
          />
          <ValidationAlert
            v-if="$v.dataForm.price.$dirty && !$v.dataForm.price.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dataForm.price.$dirty && !$v.dataForm.price.minValue"
            :text="$t('invalidDataFormat')"
          />
        </div>

        <div class="col-6">
          <label>
            {{ $t('priceForm') }}
            <span class="requared-field-star">*</span>
          </label>
          <multiselect
            v-model="dataForm.formType"
            :searchable="true"
            :placeholder="$t('priceForm')"
            :options="dataForm.formTypeList"
            :label="lang"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.formType.$dirty && !$v.dataForm.formType.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>

      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        class="col-12 text-center"
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
  </b-form>
</template>

<script src="./BackOfficeCoursePricesAdd.js" />
