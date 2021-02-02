<template>
  <b-form @submit.prevent="checkNewCertApplication">
    <b-tabs fill pills>
      <b-tab @click="checkSingleDoc(false)" active>
        <template slot="title">
          <div class="text-uppercase">
            {{ $t('positionStatement') }}
          </div>
        </template>
        <div class="d-flex wrap text-left">
          <div class="w-50">
            <label>
              {{ $t('affiliate') }}
              <span class="requared-field-star position-relative">*</span>
            </label>
            <multiselect
              v-model="dataForm.affiliate"
              @close="$v.dataForm.affiliate.$touch()"
              :options="affiliatesList"
              :searchable="true"
              :placeholder="$t('affiliate')"
              :label="labelName"
              track-by="id"
            />
            <ValidationAlert
              v-if="$v.dataForm.affiliate.$dirty && !$v.dataForm.affiliate.required"
              :text="$t('emptyField')"
            />
          </div>

          <div class="w-50">
            <label>
              {{ $t('model-SailorPassport') }}
              <span class="requared-field-star">*</span>
            </label>
            <multiselect
              v-model="dataForm.seafarerPassport"
              @close="$v.dataForm.seafarerPassport.$touch()"
              :options="processingOptionsList"
              :searchable="true"
              :placeholder="$t('model-SailorPassport')"
              :label="labelName"
            />
            <ValidationAlert
              v-if="$v.dataForm.seafarerPassport.$dirty && !$v.dataForm.seafarerPassport.required"
              :text="$t('emptyField')"
            />
          </div>

          <div class="w-50 mt-1">
            <label>
              {{ $t('qualification') }} - {{ $t('rank') }}
              <span class="required-field-star">*</span>
            </label>
            <multiselect
              v-model="dataForm.rank"
              @input="enterDoublePosition(dataForm.rank, dataForm.position) + checkTypeDocumentView()"
              @close="$v.dataForm.rank.$touch()"
              :options="ranksList"
              :label="labelName"
              :placeholder="$t('qualification') + ' - ' + $t('rank')"
              track-by="id"
            />
            <ValidationAlert
              v-if="$v.dataForm.rank.$dirty && !$v.dataForm.rank.required"
              :text="$t('emptyField')"
            />
          </div>

          <div class="w-50 mt-1">
            <label>
              {{ $t('position') }}
              <span class="requared-field-star">*</span>
            </label>
            <multiselect
              v-model="dataForm.position"
              @input="checkTypeDocumentView()"
              @remove="removePosition"
              @close="$v.dataForm.position.$touch()"
              :options="mappingAvailablePositions(dataForm.rank)"
              :searchable="true"
              :placeholder="$t('position')"
              :label="labelName"
              :max="dataForm.rank && dataForm.rank.id === 22 ? 1 : 5"
              track-by="id"
              multiple
            >
              <template slot="noOptions">
                {{ $t('selectRank') }}
              </template>
              <template slot="maxElements">
                {{ $t('maxOptionsAmount') }}
              </template>
            </multiselect>
            <ValidationAlert
              v-if="$v.dataForm.position.$dirty && !$v.dataForm.position.required"
              :text="$t('emptyField')"
            />
          </div>

          <div
            v-if="packageIsContinue !== null"
            class="w-100 mt-1 position-relative"
          >
            <label>
              {{ $t('typeDoc') }}:
              <span v-if="packageIsContinue === 1" class="requared-field-star position-relative">*</span>
            </label>
            <span v-if="packageIsContinue === 0" class="ml-1">{{ $t('documentAssignment') }}</span>
            <multiselect
              v-else-if="packageIsContinue === 1"
              v-model="dataForm.packetTypeDoc"
              @close="$v.dataForm.packetTypeDoc.$touch()"
              :options="packetTypeDocList"
              :preselect-first="true"
              :searchable="true"
              :placeholder="$t('typeDoc')"
              label="name"
              track-by="id"
            />
            <span v-else class="ml-1">{{ $t('documentAssignmentWithPosition') }}</span>
            <ValidationAlert
              v-if="$v.dataForm.packetTypeDoc.$dirty && !$v.dataForm.packetTypeDoc.required"
              :text="$t('emptyField')"
            />
          </div>

          <div
            v-if="sailorIsCadet && (dataForm.rank && (dataForm.rank.id === 23 || dataForm.rank.id === 86 || dataForm.rank.id === 90))"
            class="w-100 mt-1 text-left"
          >
            <b-form-checkbox
              v-model="dataForm.educationWithSQC"
              :value="true"
              :unchecked-value="false"
              class="mt-1 mr-1"
            >
              {{ $t('educationWithSQC') }}
            </b-form-checkbox>
          </div>

          <SailorPositionStatementPreview
            v-if="Object.keys(invalidPackageInfo).length"
            :row="invalidPackageInfo"
          />
        </div>
      </b-tab>

      <b-tab
        v-if="checkAccess('positionStatement', 'createSingleDocs')"
        @click="checkSingleDoc(true)"
      >
        <template slot="title">
          <div class="text-uppercase">
            {{ $t('documentApplication') }}
          </div>
        </template>
        <div class="d-flex wrap text-left">
          <div class="w-100 pl-1 pr-1 position-relative">
            <label>
              {{ $t('affiliate') }}
              <span class="requared-field-star">*</span>
            </label>
            <multiselect
              v-model="dataForm.affiliate"
              @close="$v.dataForm.affiliate.$touch()"
              :options="affiliatesList"
              :searchable="true"
              :placeholder="$t('affiliate')"
              :label="labelName"
              track-by="id"
            />
            <ValidationAlert
              v-if="$v.dataForm.affiliate.$dirty && !$v.dataForm.affiliate.required"
              :text="$t('emptyField')"
            />
          </div>

          <div class="w-90 mt-1 p-0">
            <label>
              {{ $t('typeDoc') }}
              <span class="requared-field-star">*</span>
            </label>
            <multiselect
              v-model="dataForm.typeDoc"
              @input="createSingleDocument"
              @close="$v.dataForm.typeDoc.$touch()"
              :options="documentsType"
              :placeholder="$t('typeDoc')"
              label="name"
              track-by="id"
            />
            <ValidationAlert
              v-if="$v.dataForm.typeDoc.$dirty && !$v.dataForm.typeDoc.required"
              :text="$t('emptyField')"
            />
          </div>
          <div class="w-10 mt-2 d-flex justify-content-center align-items-center">
            <unicon
              @click="createSingleDocument(dataForm.typeDoc)"
              name="plus"
              height="30px"
              width="30px"
              class="cursor add"
            />
          </div>

          <div
            v-if="dataForm.singleDocumentsArr.length"
            class="w-100 pl-1 pr-1 mt-1"
          >
            <div
              v-for="(record, index) of dataForm.singleDocumentsArr"
              :key="index"
              class="d-flex wrap"
            >
              <div class="w-100 p-0 mt-1">
                <label>
                  {{ $t(`model-${record.content_type}`) }}:
                </label>
                <unicon
                  @click="clearArrayDocument(index)"
                  name="multiply"
                  fill="#42627e"
                  height="20px"
                  width="20px"
                  class="close"
                />
              </div>
              <div v-if="record.content_type === 'statementeti'" class="w-33 pl-0">
                <label>
                  {{ $t('course') }}
                  <span class="requared-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.singleDocumentsArr[index].document_object.course_id"
                  @input="getInstitutionList(index)"
                  @close="$v.dataForm.singleDocumentsArr.$each[index].document_object.course_id.$touch()"
                  :options="coursesList"
                  :placeholder="$t('course')"
                  :label="labelName"
                  track-by="id"
                />
                <ValidationAlert
                  v-if="$v.dataForm.singleDocumentsArr.$each[index].document_object.course_id.$dirty &&
                   !$v.dataForm.singleDocumentsArr.$each[index].document_object.course_id.required"
                  :text="$t('emptyField')"
                />
              </div>

              <div v-if="record.content_type === 'statementeti'" class="w-33">
                <label>
                  {{ $t('city') }}
                  <span class="requared-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.singleDocumentsArr[index].document_object.city"
                  @input="getInstitutionList(index)"
                  @close="$v.dataForm.singleDocumentsArr.$each[index].document_object.city.$touch()"
                  :options="institutionsCity"
                  :searchable="true"
                  :placeholder="$t('city')"
                />
                <ValidationAlert
                  v-if="$v.dataForm.singleDocumentsArr.$each[index].document_object.city.$dirty &&
                   !$v.dataForm.singleDocumentsArr.$each[index].document_object.city.required"
                  :text="$t('emptyField')"
                />
              </div>

              <div v-if="record.content_type === 'statementeti'" class="w-33">
                <label>
                  {{ $t('nameInstitution') }}
                  <span class="requared-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.singleDocumentsArr[index].document_object.institution_id"
                  @close="$v.dataForm.singleDocumentsArr.$each[index].document_object.institution_id.$touch()"
                  :options="filteredInstitutionsList[index] ? filteredInstitutionsList[index] : []"
                  :searchable="true"
                  :placeholder="$t('nameInstitution')"
                  label="institutionName"
                >
                  <template slot="noOptions">
                <span v-if="!dataForm.singleDocumentsArr[index].document_object.course_id ||
                 !dataForm.singleDocumentsArr[index].document_object.city">
                  {{ $t('selectCourseAndCity') }}
                </span>
                    <span v-else>{{ $t('notFoundEti') }}</span>
                  </template>

                  <template slot="option" slot-scope="institution">
                  <!--  <div :class="{
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
                  v-if="$v.dataForm.singleDocumentsArr.$each[index].document_object.institution_id.$dirty &&
                   !$v.dataForm.singleDocumentsArr.$each[index].document_object.institution_id.required"
                  :text="$t('emptyField')"
                />
              </div>

              <div v-if="record.content_type === 'statementsailorpassport'" class="w-50 pl-0">
                <label>
                  {{ $t('port') }}
                  <span class="requared-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.singleDocumentsArr[index].document_object.port_id"
                  @close="$v.dataForm.singleDocumentsArr.$each[index].document_object.port_id.$touch()"
                  :options="portsList"
                  :placeholder="$t('port')"
                  :label="labelName"
                  track-by="id"
                />
                <ValidationAlert
                  v-if="$v.dataForm.singleDocumentsArr.$each[index].document_object.port_id.$dirty &&
                   !$v.dataForm.singleDocumentsArr.$each[index].document_object.port_id.required"
                  :text="$t('emptyField')"
                />
              </div>

              <div v-if="record.content_type === 'statementsailorpassport'" class="w-50">
                <label>
                  {{ $t('receiveDoc') }}
                  <span class="requared-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.singleDocumentsArr[index].document_object.type_receipt"
                  :options="validProcessingOptionsList"
                  :allow-empty="false"
                  :placeholder="$t('receiveDoc')"
                  :label="labelName"
                  track-by="id"
                />
              </div>

              <div v-if="record.content_type === 'statementmedicalcertificate'" class="w-50 pl-0">
                <label>
                  {{ $t('position') }}
                  <span class="requared-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.singleDocumentsArr[index].document_object.position_id"
                  @close="$v.dataForm.singleDocumentsArr.$each[index].document_object.position_id.$touch()"
                  :options="medicalPositionsList"
                  :placeholder="$t('position')"
                  :label="labelName"
                  track-by="id"
                />
                <ValidationAlert
                  v-if="$v.dataForm.singleDocumentsArr.$each[index].document_object.position_id.$dirty &&
                   !$v.dataForm.singleDocumentsArr.$each[index].document_object.position_id.required"
                  :text="$t('emptyField')"
                />
              </div>

              <div v-if="record.content_type === 'statementmedicalcertificate'" class="w-50">
                <label>
                  {{ $t('medicalInstitution') }}
                  <span class="requared-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.singleDocumentsArr[index].document_object.medical_institution_id"
                  @close="$v.dataForm.singleDocumentsArr.$each[index].document_object.medical_institution_id.$touch()"
                  :options="medicalInstitutionsList"
                  :placeholder="$t('medicalInstitution')"
                  label="value"
                  track-by="id"
                />
                <ValidationAlert
                  v-if="$v.dataForm.singleDocumentsArr.$each[index].document_object.medical_institution_id.$dirty &&
                   !$v.dataForm.singleDocumentsArr.$each[index].document_object.medical_institution_id.required"
                  :text="$t('emptyField')"
                />
              </div>

              <div v-if="record.content_type === 'statementadvancedtraining'" class="w-50 pl-0">
                <label>
                  {{ $t('qualification') }}
                  <span class="requared-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.singleDocumentsArr[index].document_object.level_qualification_id"
                  @close="$v.dataForm.singleDocumentsArr.$each[index].document_object.level_qualification_id.$touch()"
                  :options="qualificationLevelsList"
                  :placeholder="$t('qualification')"
                  :label="labelName"
                  track-by="id"
                />
                <ValidationAlert
                  v-if="$v.dataForm.singleDocumentsArr.$each[index].document_object.level_qualification_id.$dirty &&
                   !$v.dataForm.singleDocumentsArr.$each[index].document_object.level_qualification_id.required"
                  :text="$t('emptyField')"
                />
              </div>

              <div v-if="record.content_type === 'statementadvancedtraining'" class="w-50">
                <label>
                  {{ $t('nameInstitution') }}
                  <span class="requared-field-star">*</span>
                </label>
                <multiselect
                  v-model="dataForm.singleDocumentsArr[index].document_object.educational_institution_id"
                  @close="$v.dataForm.singleDocumentsArr.$each[index].document_object.educational_institution_id.$touch()"
                  :options="institutionsList"
                  :placeholder="$t('nameInstitution')"
                  :label="labelName"
                  track-by="id"
                />
                <ValidationAlert
                  v-if="$v.dataForm.singleDocumentsArr.$each[index].document_object.educational_institution_id.$dirty &&
                   !$v.dataForm.singleDocumentsArr.$each[index].document_object.educational_institution_id.required"
                  :text="$t('emptyField')"
                />
              </div>
            </div>
          </div>
        </div>
      </b-tab>
    </b-tabs>

    <div class="w-100 p-0 mt-1 text-left">
      <FileDropZone ref="mediaContent" />
    </div>

    <b-overlay
      :show="buttonLoader"
      spinner-variant="primary"
      opacity="0.65"
      blur="2px"
      variant="white"
      class="w-100 mt-3"
      spinner-small
    >
      <b-button
        type="submit"
        variant="success"
      >
        {{ singleDocTab ? $t('save') : canCreatePackage ? $t('save') : $t('checkValidPackage') }}
      </b-button>
    </b-overlay>
  </b-form>
</template>

<script src="./SailorPositionStatementAdd.js" />
