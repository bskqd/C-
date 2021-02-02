<template>
  <b-form @submit.prevent="checkFields">
    <div class="text-left p-1">
      <div class="flex-row-sb form-group">
        <div class="col-4">
          <label>
            {{ $t('numberProtocol') }}
            <span class="requared-field-star">*</span>
          </label>
          <b-input
            v-model="dataForm.protocolNum"
            @blur="$v.dataForm.protocolNum.$touch()"
            :placeholder="$t('numberProtocol')"
            type="number"
          />
          <ValidationAlert
            v-if="$v.dataForm.protocolNum.$dirty && !$v.dataForm.protocolNum.required"
            :text="$t('emptyField')"
          />
        </div>

        <div class="col-4">
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
                min="1900-00-01"
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
            :text="$t('invalidDataFormat')"
          />
        </div>

        <div class="col-4">
          <label>
            {{ $t('dateTermination') }}
            <span class="requared-field-star">*</span>
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateEnd"
              @blur="$v.dateEndObject.$touch()"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateEnd"
                @hidden="$v.dateEndObject.$touch()"
                :locale="lang"
                min="1900-00-01"
                max="2200-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
          <ValidationAlert
            v-if="$v.dateEndObject.$dirty && !$v.dateEndObject.required"
            :text="$t('emptyField')"
          />
          <ValidationAlert
            v-else-if="$v.dateEndObject.$dirty && (!$v.dateEndObject.maxValue || !$v.dateEndObject.minValue)"
            :text="$t('invalidDataFormat')"
          />
        </div>
      </div>

      <div class="flex-row-sb form-group">
        <div class="col-6">
          <label>
            {{ $t('nameInstitution') }}
            <span class="requared-field-star">*</span>
          </label>
          <multiselect
            v-model="dataForm.institution"
            :searchable="true"
            :placeholder="$t('nameInstitution')"
            :options="mappingInstitution"
            :label="langInstitution"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.institution.$dirty && !$v.dataForm.institution.required"
            :text="$t('emptyField')"
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
            :label="langFields"
            track-by="id"
          />
          <ValidationAlert
            v-if="$v.dataForm.course.$dirty && !$v.dataForm.course.required"
            :text="$t('emptyField')"
          />
        </div>
      </div>

      <div class="col-12 form-group">
        <b-form-checkbox
          v-model="dataForm.isDisable"
          :value="true"
          :unchecked-value="false"
          class="mt-1 mr-1"
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
        class="w-100 text-center"
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

<script src="./BackOfficeCoursesAdd.js" />

<style scoped>

</style>
