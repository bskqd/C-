<template>
    <div class="disable-rounded-right p-2">
      <div class="card-header">
        <div class="card-title d-flex justify-content-center">
          <h4 class="text-center">
            {{ $t('search') }}
          </h4>
          <div class="search-btns position-absolute text-right">
            <unicon
              v-if="viewSearch"
              @click="viewSearch = !viewSearch"
              name="angle-up"
              width="40px"
              height="40px"
              fill="royalblue"
            />
            <unicon
              v-if="!viewSearch"
              @click="viewSearch = !viewSearch"
              name="angle-down"
              width="40px"
              height="40px"
              fill="royalblue"
            />
          </div>
        </div>
      </div>
      <div
        v-if="viewSearch"
        class="d-flex wrap card-content text-left pt-3"
      >
        <div
          v-if="sqcApplication || sqcProtocol || etiCertificate || education || qualDocument || qualApplication ||
           finance || report === 'debtor' || agentStatements || srbStatements || report === 'distribution' ||
           statementETI || etiPayments || userHistory || statementAdvanceTraining || newAccounts || sailorPassport"
          class="w-100 mb-1 d-flex p-0"
        >
          <div
            v-if="report === 'distribution'"
            class="w-50"
          >
            <label>
              {{ $t('type') }}
            </label>
            <multiselect
              v-model="dataForm.distributionType"
              @input="allowSaveExcel = true"
              :preselectFirst="true"
              :allow-empty="false"
              :options="mappingDistributionType"
              label="name"
              track-by="id"
            />
          </div>
          <div
            v-if="finance || agentStatements"
            class="w-25"
          >
            <label>
              {{ $t('exactDate') }}
            </label>
            <b-input-group>
              <b-form-input
                v-model="dataForm.exactDate"
                @input="allowSaveExcel = true"
                type="date"
              />
              <b-input-group-append>
                <b-form-datepicker
                  v-model="dataForm.exactDate"
                  @input="allowSaveExcel = true"
                  :locale="lang"
                  :max="new Date()"
                  min="1900-01-01"
                  start-weekday="1"
                  button-only
                  right
                />
              </b-input-group-append>
            </b-input-group>
          </div>
          <div class="w-25">
            <label>
              {{ $t('periodStart') }}
            </label>
            <b-input-group>
              <b-form-input
                v-model="dataForm.periodStart"
                @input="allowSaveExcel = true"
                type="date"
              />
              <b-input-group-append>
                <b-form-datepicker
                  v-model="dataForm.periodStart"
                  @input="allowSaveExcel = true"
                  :locale="lang"
                  :max="new Date()"
                  min="1900-01-01"
                  start-weekday="1"
                  button-only
                  right
                />
              </b-input-group-append>
            </b-input-group>
          </div>
          <div class="w-25">
            <label>
              {{ $t('periodEnd') }}
            </label>
            <b-input-group>
              <b-form-input
                v-model="dataForm.periodEnd"
                @input="allowSaveExcel = true"
                type="date"
              />
              <b-input-group-append>
                <b-form-datepicker
                  v-model="dataForm.periodEnd"
                  @input="allowSaveExcel = true"
                  :locale="lang"
                  :max="new Date()"
                  min="1900-01-01"
                  start-weekday="1"
                  button-only
                  right
                />
              </b-input-group-append>
            </b-input-group>
          </div>
<!--          <div-->
<!--            v-if="sqcApplication"-->
<!--            class="w-50"-->
<!--          >-->
<!--            <label>-->
<!--              {{ $t('statementType') }}-->
<!--            </label>-->
<!--            <multiselect-->
<!--              v-model="dataForm.protocolAvailability"-->
<!--              @input="allowSaveExcel = true"-->
<!--              :preselectFirst="true"-->
<!--              :allow-empty="false"-->
<!--              :options="mappingProtocolAvailability"-->
<!--              label="name"-->
<!--              track-by="id"-->
<!--            />-->
<!--          </div>-->
          <div
            v-if="(sqcApplication || reportCadet) && dataForm.statementAvailability && dataForm.statementAvailability.id === 2"
            class="w-50 mb-1"
          >
            <label>
              {{ $t('protocolAvailability') }}
            </label>
            <multiselect
              v-model="dataForm.protocolAvailability"
              @input="allowSaveExcel = true"
              :preselectFirst="true"
              :allow-empty="false"
              :options="mappingProtocolAvailability"
              label="name"
              track-by="id"
            />
          </div>
        </div>

        <div
          v-if="report === 'distribution'"
          class="w-50"
        >
          <label>
            {{ $t('getDocStatus') }}
          </label>
          <multiselect
            v-model="dataForm.getDocumentStatus"
            @input="allowSaveExcel = true"
            :preselectFirst="true"
            :allow-empty="false"
            :options="listGetDocumentStatus"
            label="name"
            track-by="id"
          />
        </div>
        <div v-if="dataForm.getDocumentStatus && dataForm.getDocumentStatus.id === 1" class="w-25">
          <label>
            {{ $t('periodStartReceipt') }}
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.periodStartReceipt"
              @input="allowSaveExcel = true"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.periodStartReceipt"
                @input="allowSaveExcel = true"
                :locale="lang"
                :max="new Date()"
                min="1900-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
        </div>
        <div v-if="dataForm.getDocumentStatus && dataForm.getDocumentStatus.id === 1" class="w-25">
          <label>
            {{ $t('periodEndReceipt') }}
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.periodEndReceipt"
              @input="allowSaveExcel = true"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.periodEndReceipt"
                @input="allowSaveExcel = true"
                :locale="lang"
                :max="new Date()"
                min="1900-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
        </div>

        <div
          v-if="sqcProtocol || (sqcApplication && dataForm.protocolAvailability && dataForm.protocolAvailability.id !== 3)"
          class="w-40 mb-1"
        >
          <label>
            {{ $t('numberProtocol') }} / {{ $t('year') }}
          </label>
          <b-form-input
            v-model="dataForm.numberProtocol"
            @input="allowSaveExcel = true"
            @blur="$v.dataForm.numberProtocol.$touch()"
            placeholder="_____/____"
          />
          <ValidationAlert
            v-if="$v.dataForm.numberProtocol.$dirty && !$v.dataForm.numberProtocol.regexpNumber"
            :text="$t('regexpNumber')"
          />
        </div>

        <div
          v-if="sqcProtocol || (sqcApplication && dataForm.protocolAvailability && dataForm.protocolAvailability.id !== 3)"
          class="w-40 mb-1"
        >
          <label>
            {{ $t('affiliate') }}
          </label>
          <multiselect
            v-model="dataForm.affiliate"
            @input="allowSaveExcel = true"
            :searchable="true"
            :options="mappingAffiliate"
            :placeholder="$t('affiliate')"
            :label="labelName"
            track-by="id"
            multiple
          />
        </div>
        <div
          v-if="sqcProtocol || sqcApplication"
          :class="{ 'w-20': sqcProtocol, 'w-50': sqcApplication }"
          class="mb-1"
        >
          <label>
            {{ $t('way') }}
          </label>
          <multiselect
            v-model="dataForm.protocolWay"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('way')"
            :options="mappingWay"
            :label="labelName"
            track-by="name_ukr"
            multiple
          />
        </div>
<!--        <div-->
<!--          v-if="sqcApplication && dataForm.protocolAvailability"-->
<!--          :class="{ 'mb-1 w-20': dataForm.protocolAvailability.id !== 3, 'mb-1 w-100 pl-1 pr-1': dataForm.protocolAvailability.id === 3 }"-->
<!--        >-->
<!--          <label>-->
<!--            {{ $t('specialty') }}-->
<!--          </label>-->
<!--          <multiselect-->
<!--            v-model="dataForm.specialty"-->
<!--            @input="allowSaveExcel = true"-->
<!--            :searchable="true"-->
<!--            :placeholder="$t('specialty')"-->
<!--            :options="mappingWay"-->
<!--            :label="labelName"-->
<!--            track-by="name_ukr"-->
<!--            multiple-->
<!--          />-->
<!--        </div>-->
        <div
          v-if="sqcProtocol || sqcApplication"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('numberStatement') }} / {{ $t('year') }}
          </label>
          <b-form-input
            v-model="dataForm.numberStatement"
            @input="allowSaveExcel = true"
            @blur="$v.dataForm.numberStatement.$touch()"
            placeholder="_____/____"
          />
          <ValidationAlert
            v-if="$v.dataForm.numberStatement.$dirty && !$v.dataForm.numberStatement.regexpNumber"
            :text="$t('regexpNumber')"
          />
        </div>
        <div
          v-if="sqcProtocol || sqcApplication"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('affiliate') }}
          </label>
          <multiselect
            v-model="dataForm.statementAffiliate"
            @input="allowSaveExcel = true"
            :searchable="true"
            :options="mappingAffiliate"
            :placeholder="$t('affiliate')"
            :label="labelName"
            track-by="id"
            multiple
          />
        </div>

        <div
          v-if="finance || agentStatements || statementETI || etiPayments || statementAdvanceTraining || sailorPassport"
          class="w-33"
          :class="{ 'w-25': statementETI || etiPayments || statementAdvanceTraining || sailorPassport, 'w-33': !statementETI }"
        >
          <label>
            {{ $t('sailorId') }}
          </label>
          <b-form-input
            v-model="dataForm.sailorId"
            @input="allowSaveExcel = true"
            :placeholder="$t('sailorId')"
            type="number"
          />
        </div>

        <div
          v-if="sqcApplication || sqcProtocol || etiCertificate || reportCadet || qualDocument || qualApplication ||
           agentStatements || srbStatements || statementETI || etiPayments || statementAdvanceTraining || newAccounts ||
           sailorPassport"
          class="w-33 mb-1"
          :class="{ 'w-25': statementETI && !agentStatements, 'w-75': etiPayments || statementAdvanceTraining || sailorPassport,
           'w-50': !agentStatements && !statementETI, 'w-100': newAccounts }"
        >
          <label>
            {{ $t('sailorFullName') }}
          </label>
          <b-form-input
            v-model="dataForm.fullName"
            @input="allowSaveExcel = true"
            :placeholder="$t('sailorFullName')"
            type="text"
          />
        </div>

        <div
          v-if="(userId !== 14365 && userId !== 14488) && agentStatements"
          class="w-33 mb-1"
        >
          <label>
            {{ $t('nameEmployee') }}
          </label>
          <b-form-input
            v-model="dataForm.agentFullName"
            @input="allowSaveExcel = true"
            :placeholder="$t('nameEmployee')"
            type="text"
          />
        </div>

        <div
          v-if="agentStatements"
          class="w-33 mb-1"
        >
          <label>
            {{ $t('contractDateEnd') }}
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateEndProxy"
              @input="allowSaveExcel = true"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateEndProxy"
                @input="allowSaveExcel = true"
                :locale="lang"
                max="2200-01-01"
                min="1900-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
        </div>

        <div
          v-if="agentStatements"
          class="w-33 mb-1"
        >
          <label>
            {{ $t('periodStart') }}
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateEndProxyFrom"
              @input="allowSaveExcel = true"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateEndProxyFrom"
                @input="allowSaveExcel = true"
                :locale="lang"
                max="2200-01-01"
                min="1900-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
        </div>

        <div
          v-if="agentStatements"
          class="w-33 mb-1"
        >
          <label>
            {{ $t('periodEnd') }}
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateEndProxyTo"
              @input="allowSaveExcel = true"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateEndProxyTo"
                @input="allowSaveExcel = true"
                :locale="lang"
                max="2200-01-01"
                min="1900-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
        </div>

        <div
          v-if="sqcApplication || sqcProtocol || etiCertificate || reportCadet || qualDocument || qualApplication"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('dateBorn') }}
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateBorn"
              @input="allowSaveExcel = true"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateBorn"
                @input="allowSaveExcel = true"
                :locale="lang"
                :max="new Date()"
                min="1900-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
        </div>

        <div
          v-if="education"
          class="w-100 mb-1"
        >
          <label>
            {{ $t('typeDoc') }}
          </label>
          <multiselect
            v-model="dataForm.typeDoc"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('typeDoc')"
            :options="mappingTypeDoc"
            :label="labelName"
            track-by="id"
          />
        </div>

        <div
          v-if="finance"
          class="w-33"
        >
          <label>
            {{ $t('typeDoc') }}
          </label>
          <multiselect
            v-model="dataForm.accrualTypeDoc"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('typeDoc')"
            :options="allAccrualTypeDoc"
            label="value"
            track-by="id"
            multiple
          />
        </div>

        <div
          v-if="qualDocument || finance"
          :class="{ 'w-50': qualDocument, 'w-33': finance }"
        >
          <label>
            {{ $t('number') }}
          </label>
          <b-form-input
            v-model="dataForm.number"
            @input="allowSaveExcel = true"
            :placeholder="$t('number')"
            type="text"
          />
        </div>

        <div
          v-if="finance"
          class="w-100 mb-1"
        >
          <label>
            {{ $t('price') }} {{ $t('firstForm') }}
          </label>
          <div class="w-100 d-flex justify-content-sb bv-no-focus-ring p-0">
            <b-form-input
              v-model="dataForm.firstFormSum"
              @input="allowSaveExcel = true"
              :placeholder="`${$t('price')} ${$t('firstForm')}`"
              type="number"
              class="w-33"
            />
            <b-form-radio-group
              v-model="dataForm.firstFormParams"
              :options="formParams"
              class="w-70"
            />
          </div>
        </div>

        <div
          v-if="finance"
          class="w-100 mb-1"
        >
          <label>
            {{ $t('price') }} {{ $t('secondForm') }}
          </label>
          <div class="w-100 d-flex justify-content-sb bv-no-focus-ring p-0">
            <b-form-input
              v-model="dataForm.secondFormSum"
              @input="allowSaveExcel = true"
              :placeholder="`${$t('price')} ${$t('secondForm')}`"
              type="number"
              class="w-33"
            />
            <b-form-radio-group
              v-model="dataForm.secondFormParams"
              :options="formParams"
              class="w-70"
            />
          </div>
        </div>

        <div
          v-if="qualDocument"
          class="w-50"
        >
          <label>
            {{ $t('typeDoc') }}
          </label>
          <multiselect
            v-model="dataForm.typeQualDoc"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('typeDoc')"
            :options="mappingTypeDocQualification"
            :label="labelName"
            track-by="id"
          />
        </div>

        <div
          v-if="qualDocument || sailorPassport"
          class="w-50"
        >
          <label>
            {{ $t('country') }}
          </label>
          <multiselect
            v-model="dataForm.country"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('country')"
            :options="mappingCountry"
            :label="labelValue"
            track-by="id"
            multiple
          />
        </div>

        <div
          v-if="qualDocument || sailorPassport"
          class="w-50"
        >
          <label>
            {{ $t('port') }}
          </label>
          <multiselect
            v-if="viewPortSelect"
            v-model="dataForm.port"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('port')"
            :options="mappingPorts"
            :label="labelName"
            track-by="id"
            multiple
          />
          <b-form-input
            v-else
            v-model="dataForm.otherPort"
            @input="allowSaveExcel = true"
            :placeholder="$t('port')"
            type="text"
          />
        </div>

        <div
          v-if="education"
          class="w-33 mb-1"
        >
          <label>
            {{ $t('registrationNumber') }}
          </label>
          <b-input
            v-model="dataForm.registrationNumber"
            @input="allowSaveExcel = true"
            :placeholder="$t('registrationNumber')"
            type="text"
          />
        </div>

        <div
          v-if="education"
          class="w-33 mb-1"
        >
          <label>
            {{ $t('serial') }}
          </label>
          <b-input
            v-model="dataForm.serial"
            @input="allowSaveExcel = true"
            :placeholder="$t('serial')"
            type="text"
          />
        </div>

        <div
          v-if="education"
          class="w-33 mb-1"
        >
          <label>
            {{ $t('number') }}
          </label>
          <b-input
            v-model="dataForm.graduationNumber"
            @input="allowSaveExcel = true"
            :placeholder="$t('number')"
            type="text"
          />
        </div>

        <div
          v-if="etiCertificate"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('number') }}
          </label>
          <b-form-input
            v-model="dataForm.certificateNumber"
            @input="allowSaveExcel = true"
            :placeholder="$t('number')"
            type="text"
          />
        </div>

        <div
          v-if="education"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('educationExtent') }}
          </label>
          <multiselect
            v-model="dataForm.educationExtent"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('educationExtent')"
            :options="mappingExtent"
            :label="labelName"
            track-by="id"
            multiple
          />
        </div>

        <div
          v-if="education || reportCadet || (statementAdvanceTraining && checkAccess('backOffice'))"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('nameInstitution') }}
          </label>
          <multiselect
            v-model="dataForm.institution"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('nameInstitution')"
            :options="mappingInstitution"
            :label="labelName"
            track-by="id"
            multiple
          />
        </div>

        <div
          v-if="statementAdvanceTraining"
          class="w-50 mb-1"
          :class="{ 'w-100': !checkAccess('backOffice') }"
        >
          <label>
            {{ $t('qualification') }}
          </label>
          <multiselect
            v-model="dataForm.qualificationLevel"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('qualification')"
            :options="mappingQualificationLevels"
            :label="labelName"
            track-by="id"
            multiple
          />
        </div>

        <div
          v-if="reportCadet"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('way') }}
          </label>
          <multiselect
            v-model="dataForm.cadetFaculty"
            @input="allowSaveExcel = true"
            :placeholder="$t('way')"
            :options="mappingFaculties"
            :label="labelName"
            track-by="id"
            multiple
          />
        </div>

        <div
          v-if="education"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('qualification') }}
          </label>
          <multiselect
            v-model="dataForm.qualification"
            @input="allowSaveExcel = true"
            :options="mappingQualification"
            :searchable="true"
            :placeholder="$t('qualification')"
            :label="labelName"
            track-by="id"
            multiple
          />
        </div>

        <div
          v-if="education"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('specialty') }}
          </label>
          <multiselect
            v-model="dataForm.specialty"
            @input="allowSaveExcel = true"
            :options="mappingProfession"
            :searchable="true"
            :placeholder="$t('specialty')"
            :label="labelName"
            track-by="id"
            multiple
          />
        </div>

        <div
          v-if="education"
          class="w-100 mb-1"
        >
          <label>
            {{ $t('specialization') }}
          </label>
          <multiselect
            v-model="dataForm.specialization"
            @input="allowSaveExcel = true"
            :options="mappingSpecialization"
            :searchable="true"
            :placeholder="$t('specialization')"
            :label="labelName"
            track-by="id"
            multiple
          />
        </div>

        <div
          v-if="etiCertificate || statementETI || etiPayments"
          :class="{ 'w-50 mb-1': !etiPayments, 'w-100 px-4': etiPayments }"
        >
          <label>
            {{ $t('course') }}
          </label>
          <multiselect
            v-model="dataForm.certificateCourse"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('course')"
            :options="mappingCourses"
            :label="labelName"
            track-by="id"
            multiple
          />
        </div>

        <div
          v-if="userHistory"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('user') }}
          </label>
          <multiselect
            v-model="dataForm.user"
            :searchable="true"
            :options="usersList"
            :placeholder="$t('user')"
            label="userFullName"
            track-by="id"
          />
        </div>

        <div
          v-if="userHistory"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('sailor') }}
          </label>
          <multiselect
            v-model="dataForm.sailor"
            @search-change="startSearch"
            :searchable="true"
            :options="dataForm.sailorsSearchList"
            :placeholder="$t('goSearch')"
            label="sailorFullName"
            track-by="id"
          />
        </div>

        <div
          v-if="etiCertificate || (checkAccess('backOffice') && (statementETI || etiPayments))"
          class="w-100 mb-1 px-3"
        >
          <label>
            {{ $t('nameInstitution') }}
          </label>
          <multiselect
            v-model="dataForm.educationInstitution"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('nameInstitution')"
            :options="mappingTrainingPlace"
            :label="labelName"
            track-by="id"
            multiple
          />
        </div>

        <div
          v-if="etiCertificate || education || qualDocument || qualApplication"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('dateIssue') }}
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateIssue"
              @input="allowSaveExcel = true"
              max="2200-01-01"
              min="1900-01-01"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateIssue"
                @input="allowSaveExcel = true"
                :locale="lang"
                max="2200-01-01"
                min="1900-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
        </div>

        <div
          v-if="etiCertificate || education || qualDocument || qualApplication"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('dateTermination') }}
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateTerminate"
              @input="allowSaveExcel = true"
              max="2200-01-01"
              min="1900-01-01"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateTerminate"
                @input="allowSaveExcel = true"
                :locale="lang"
                max="2200-01-01"
                min="1900-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
        </div>

        <div
          v-if="sqcProtocol || sqcApplication || qualDocument || qualApplication"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('rank') }}
          </label>
          <multiselect
            v-model="dataForm.rank"
            @input="changeRank(dataForm.rank)"
            :searchable="true"
            :placeholder="$t('rank')"
            :options="mappingRank"
            :label="labelName"
            track-by="id"
            multiple
          />
        </div>
        <div
          v-if="sqcProtocol || sqcApplication || medical || qualDocument || qualApplication"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('position') }}
          </label>
          <multiselect
            v-model="dataForm.position"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('position')"
            :options="mappingPosition(dataForm.rank)"
            :label="labelName"
            track-by="id"
            multiple
          >
            <span slot="noOptions">
              {{ $t('selectRank') }}
            </span>
          </multiselect>
        </div>

        <div
          v-if="statementETI || statementAdvanceTraining"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('dateStartEduFrom') }}
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.meetingDateFrom"
              @input="allowSaveExcel = true"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.meetingDateFrom"
                @input="allowSaveExcel = true"
                :locale="lang"
                max="2200-01-01"
                min="1900-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
        </div>

        <div
          v-if="statementETI || statementAdvanceTraining"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('dateStartEduTo') }}
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.meetingDateTo"
              @input="allowSaveExcel = true"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.meetingDateTo"
                @input="allowSaveExcel = true"
                :locale="lang"
                max="2200-01-01"
                min="1900-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
        </div>

        <div
          v-if="statementETI || statementAdvanceTraining"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('dateEndEduFrom') }}
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.meetingDateEndFrom"
              @input="allowSaveExcel = true"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.meetingDateEndFrom"
                @input="allowSaveExcel = true"
                :locale="lang"
                max="2200-01-01"
                min="1900-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
        </div>

        <div
          v-if="statementETI || statementAdvanceTraining"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('dateEndEduTo') }}
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.meetingDateEndTo"
              @input="allowSaveExcel = true"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.meetingDateEndTo"
                @input="allowSaveExcel = true"
                :locale="lang"
                max="2200-01-01"
                min="1900-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
        </div>

        <div
          v-if="sqcProtocol"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('headCommission') }}
          </label>
          <multiselect
            v-model="dataForm.headCommissioner"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('headCommission')"
            :options="allCommissioners"
            label="fullName"
            multiple
          />
        </div>
        <div
          v-if="sqcProtocol"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('membersCommission') }}
          </label>
          <multiselect
            v-model="dataForm.memberCommissioner"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('membersCommission')"
            :options="allCommissioners"
            label="fullName"
            multiple
          />
        </div>
        <div
          v-if="(userId !== 14365 && userId !== 14488) && (sqcProtocol || sqcApplication)"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('requirementExperience') }}
          </label>
          <multiselect
            v-model="dataForm.experience"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('requirementExperience')"
            :options="mappingExperience"
            :label="labelName"
            track-by="value"
            multiple
          />
        </div>
        <div
          v-if="sqcProtocol"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('solution') }}
          </label>
          <multiselect
            v-model="dataForm.solution"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('solution')"
            :options="mappingSolution"
            label="name"
            track-by="value"
            multiple
          />
        </div>

        <div
          v-if="reportCadet"
          :class="{ 'mb-1 w-50': dataForm.statementAvailability && dataForm.statementAvailability.id === 2,
           'mb-1 w-100': dataForm.statementAvailability && dataForm.statementAvailability.id !== 2 }"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('statementAvailability') }}
          </label>
          <multiselect
            v-model="dataForm.statementAvailability"
            @input="allowSaveExcel = true"
            :preselectFirst="true"
            :allow-empty="false"
            :options="mappingApplicationAvailability"
            label="name"
            track-by="id"
          />
        </div>

        <div
          v-if="sqcApplication"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('protocolAvailability') }}
          </label>
          <multiselect
            v-model="dataForm.protocolAvailability"
            @input="allowSaveExcel = true"
            :preselectFirst="true"
            :allow-empty="false"
            :placeholder="$t('protocolAvailability')"
            :options="mappingProtocolAvailability"
            label="name"
            track-by="id"
          />
        </div>

        <div
          v-if="reportCadet"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('resultEKK') }}
          </label>
          <multiselect
            v-model="dataForm.resultEQC"
            @input="allowSaveExcel = true"
            :preselectFirst="true"
            :allow-empty="false"
            :options="mappingResultsEQC"
            label="name"
            track-by="id"
          />
        </div>

        <div
          v-if="reportCadet"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('decisionEKK') }}
          </label>
          <multiselect
            v-model="dataForm.educPassedExam"
            @input="allowSaveExcel = true"
            :preselectFirst="true"
            :allow-empty="false"
            :options="mappingEducExamPass"
            label="name"
            track-by="id"
          />
        </div>

<!--        <div-->
<!--          v-if="reportCadet || statementAdvanceTraining"-->
<!--          class="w-50 mb-1"-->
<!--        >-->
<!--          <label>-->
<!--            {{ $t('nameInstitution') }}-->
<!--          </label>-->
<!--          <multiselect-->
<!--            v-model="dataForm.institution"-->
<!--            @input="allowSaveExcel = true"-->
<!--            :placeholder="$t('nameInstitution')"-->
<!--            :options="mappingInstitution"-->
<!--            :label="labelName"-->
<!--            track-by="id"-->
<!--            multiple-->
<!--          />-->
<!--        </div>-->

        <div
          v-if="sqcApplication"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('dateEventFrom') }}
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateMeetingFrom"
              @input="allowSaveExcel = true"
              max="2200-01-01"
              min="1900-01-01"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateMeetingFrom"
                @input="allowSaveExcel = true"
                :locale="lang"
                max="2200-01-01"
                min="1900-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
        </div>
        <div
          v-if="sqcApplication"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('dateEventTo') }}
          </label>
          <b-input-group>
            <b-form-input
              v-model="dataForm.dateMeetingTo"
              @input="allowSaveExcel = true"
              max="2200-01-01"
              min="1900-01-01"
              type="date"
            />
            <b-input-group-append>
              <b-form-datepicker
                v-model="dataForm.dateMeetingTo"
                @input="allowSaveExcel = true"
                :locale="lang"
                max="2200-01-01"
                min="1900-01-01"
                start-weekday="1"
                button-only
                right
              />
            </b-input-group-append>
          </b-input-group>
        </div>

        <div
          v-if="(userId !== 14365 && userId !== 14488) && ((sqcApplication || sqcProtocol || sailorPassport) && checkAccess('backOffice'))"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('agentsDocument') }}
          </label>
          <multiselect
            v-model="dataForm.withoutDate"
            @input="allowSaveExcel = true"
            :placeholder="$t('agentsDocument')"
            :options="mappingBooleanOptions"
            label="name"
            track-by="id"
          />
        </div>

        <div
          v-if="sailorPassport"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('newDocument') }}
          </label>
          <multiselect
            v-model="dataForm.newDocument"
            @input="allowSaveExcel = true"
            :placeholder="$t('newDocument')"
            :options="mappingBooleanOptions"
            label="name"
            track-by="id"
          />
        </div>

        <div
          v-if="sailorPassport"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('statementType') }}
          </label>
          <multiselect
            v-model="dataForm.statementType"
            @input="allowSaveExcel = true"
            :placeholder="$t('statementType')"
            :options="mappingStatementTypes"
            label="name"
            track-by="id"
          />
        </div>

        <div
          v-if="(userId !== 14365 && userId !== 14488) && (sqcApplication || sqcProtocol)"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('cadet') }}
          </label>
          <multiselect
            v-model="dataForm.isCadet"
            @input="allowSaveExcel = true"
            :placeholder="$t('cadet')"
            :options="mappingCadetType"
            :preselectFirst="true"
            :allow-empty="false"
            label="name"
            track-by="id"
          />
        </div>

        <div
          v-if="srbStatements || statementETI || statementAdvanceTraining"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('payment') }}
          </label>
          <multiselect
            v-model="dataForm.payment"
            @input="allowSaveExcel = true"
            :placeholder="$t('payment')"
            :options="paymentStatus"
            :label="labelName"
            track-by="id"
          />
        </div>

        <div
          v-if="sqcApplication|| qualDocDiploma || qualDocCert || graduationCert ||
            education || medical || seafarerPassport || citizenPassport || qualDocument ||
            qualApplication || agentStatements || srbStatements || statementETI || statementAdvanceTraining || sailorPassport"
          class="w-50 mb-1"
        >
          <label>
            {{ $t('status') }}
          </label>
          <multiselect
            v-model="dataForm.status"
            @input="allowSaveExcel = true"
            :searchable="true"
            :placeholder="$t('status')"
            :options="mappingStatuses"
            :label="labelName"
            track-by="id"
            multiple
          />
        </div>

        <div class="w-100 d-flex justify-content-around mt-1">
          <b-button
            @click="setParams('report')"
            variant="success"
          >
            {{ $t('search') }}
          </b-button>

          <b-button
            v-show="allowSaveExcel && (sqcProtocol || sqcApplication || etiCertificate)"
            @click="setParams('excel')"
            variant="outline-primary"
          >
            {{ $t('saveAsExcel') }}
          </b-button>
        </div>
      </div>
      <div v-if="resultSearchTitle.length">
        {{ resultSearchTitle.join('; ') }}
      </div>
  </div>
</template>

<script src="./ReportSearch.js"/>

<style scoped>
  .search-btns {
    right: 3vw;
    cursor: pointer;
  }
</style>
