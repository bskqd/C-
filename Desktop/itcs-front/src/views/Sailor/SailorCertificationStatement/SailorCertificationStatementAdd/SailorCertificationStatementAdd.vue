<template>
  <b-form @submit.prevent="validateForm">
    <div class="d-flex wrap text-left">
      <div class="w-50">
        <label>
          {{ $t('course') }}
          <span class="requared-field-star">*</span>
        </label>
        <multiselect
          v-model="dataForm.course"
          @input="mappingCertApplicationInstitution"
          @close="$v.dataForm.course.$touch()"
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

      <div class="w-50">
        <label>
          {{ $t('city') }}
          <span class="requared-field-star">*</span>
        </label>
        <multiselect
          v-model="dataForm.city"
          @input="mappingCertApplicationInstitution"
          @close="$v.dataForm.city.$touch()"
          :searchable="true"
          :placeholder="$t('city')"
          :options="institutionsCity"
        />
        <ValidationAlert
          v-if="$v.dataForm.city.$dirty && !$v.dataForm.city.required"
          :text="$t('emptyField')"
        />
      </div>

      <div class="w-100 mt-1 position-relative">
        <label>
          {{ $t('nameInstitution') }}
          <span class="requared-field-star">*</span>
        </label>
        <multiselect
          v-model="dataForm.eti"
          @close="$v.dataForm.eti.$touch()"
          :options="filteredInstitutionsList[0] ? filteredInstitutionsList[0] : []"
          :searchable="true"
          :placeholder="$t('nameInstitution')"
          label="institutionName"
        >
          <template slot="noOptions">
            <span v-if="!dataForm.course || !dataForm.city">{{ $t('selectCourseAndCity') }}</span>
            <span v-else>{{ $t('notFoundEti') }}</span>
          </template>

          <template slot="option" slot-scope="institution">
            <!--<div :class="{
              'green-option': institution.option.status === 'green-option',
              'grey-option': institution.option.status === 'grey-option',
              'red-option': institution.option.status === 'red-option'
            }">
              {{ institution.option.institutionName }}
              <span v-if="institution.option.status === 'green-option'">{{ $t('fastProcessing') }}</span>
              <span v-else-if="institution.option.status === 'grey-option'">{{ $t('normalProcessing') }}</span>
              <span v-else>{{ $t('slowProcessing') }}</span>
            </div>-->
            {{ institution.option.institutionName }}
          </template>
        </multiselect>
        <ValidationAlert
          v-if="$v.dataForm.eti.$dirty && !$v.dataForm.eti.required"
          :text="$t('emptyField')"
        />
      </div>

      <b-overlay
        :show="buttonLoader"
        spinner-variant="primary"
        opacity="0.65"
        blur="2px"
        variant="white"
        class="w-100 text-center mt-2"
        spinner-small
      >
        <b-button
          type="submit"
          variant="success"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </div>
  </b-form>

</template>

<script src="./SailorCertificationStatementAdd.js"/>
