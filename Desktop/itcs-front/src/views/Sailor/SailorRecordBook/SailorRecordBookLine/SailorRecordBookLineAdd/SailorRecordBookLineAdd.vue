<template>
  <b-card header-tag="header">
    <b-form
      @submit.prevent="checkSavingNewEntry"
      class="text-left d-flex wrap"
    >
      <div class="text-left w-100">
        <h5 class="text-bold-600">
          {{ $t('infoShip') }}:
        </h5>
        <div class="flex-row-sb form-group">
          <div class="col-4">
            <label>
              {{ $t('numShip') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input
              v-model="dataForm.numShip"
              @blur="$v.dataForm.numShip.$touch()"
              :placeholder="$t('numShip')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.numShip.$dirty && !$v.dataForm.numShip.required)"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.numShip.$dirty && !$v.dataForm.numShip.maxLength)"
              :text="$t('tooLongNumber')"
            />
          </div>
          <div class="col-4">
            <label>
              {{ $t('nameShip') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input
              v-model="dataForm.nameShip"
              @blur="$v.dataForm.nameShip.$touch()"
              :placeholder="$t('nameShip')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.nameShip.$dirty && !$v.dataForm.nameShip.required)"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.nameShip.$dirty && !$v.dataForm.nameShip.maxLength)"
              :text="$t('shipNameLength')"
            />
          </div>
          <div class="col-4">
            <label>
              {{ $t('typeShip') }}
              <span class="required-field-star">*</span>
            </label>
            <multiselect
              v-model="dataForm.typeShip"
              @close="$v.dataForm.typeShip.$touch()"
              :options="mappingTypeShip"
              :searchable="true"
              :placeholder="$t('typeShip')"
              :label="labelName"
              track-by="id"
            />
            <ValidationAlert
              v-if="($v.dataForm.typeShip.$dirty && !$v.dataForm.typeShip.required)"
              :text="$t('emptyField')"
            />
          </div>
        </div>

        <div class="flex-row-sb form-group mt-2">
          <div class="col-6">
            <label>
              {{ $t('modeShipping') }}
              <span class="required-field-star">*</span>
            </label>
            <multiselect
              v-model="dataForm.modeShipping"
              @close="$v.dataForm.modeShipping.$touch()"
              :options="mappingModeShipping"
              :searchable="true"
              :placeholder="$t('modeShipping')"
              :label="labelName"
              track-by="id"
            />
            <ValidationAlert
              v-if="($v.dataForm.modeShipping.$dirty && !$v.dataForm.modeShipping.required)"
              :text="$t('emptyField')"
            />
          </div>
          <div class="col-6">
            <label>
              {{ $t('portShip') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input
              v-model="dataForm.portShip"
              @blur="$v.dataForm.portShip.$touch()"
              :placeholder="$t('portShip')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.portShip.$dirty && !$v.dataForm.portShip.required)"
              :text="$t('emptyField')"
            />
          </div>
        </div>

        <div class="flex-row-sb form-group mt-2">
          <div class="col-12">
            <label>
              {{ $t('ownerShip') }}
            </label>
            <b-input
              v-model="dataForm.ownerShip"
              @blur="$v.dataForm.ownerShip.$touch()"
              :placeholder="$t('ownerShip')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.ownerShip.$dirty && !$v.dataForm.ownerShip.maxLength)"
              :text="$t('tooLongCaptName')"
            />
          </div>
        </div>

        <div class="flex-row-sb form-group mt-2">
          <div class="col-3">
            <label>
              {{ $t('grossCapacity') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input
              v-model="dataForm.grossCapacity"
              @blur="$v.dataForm.grossCapacity.$touch()"
              :placeholder="$t('grossCapacity')"
              type="number"
            />
            <ValidationAlert
              v-if="($v.dataForm.grossCapacity.$dirty && !$v.dataForm.grossCapacity.required)"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.grossCapacity.$dirty && !$v.dataForm.grossCapacity.numeric)"
              :text="$t('onlyNumeric')"
            />
          </div>
          <div class="col-3">
            <label>
              {{ $t('powerGEU') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input
              v-model="dataForm.powerGEU"
              @blur="$v.dataForm.powerGEU.$touch()"
              :placeholder="$t('powerGEU')"
              type="number"
            />
            <ValidationAlert
              v-if="($v.dataForm.powerGEU.$dirty && !$v.dataForm.powerGEU.required)"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.powerGEU.$dirty && !$v.dataForm.powerGEU.numeric)"
              :text="$t('onlyNumeric')"
            />
          </div>
          <div class="col-3">
            <label>
              {{ $t('coldProductivity') }}
            </label>
            <b-input
              v-model="dataForm.coldProductivity"
              @blur="$v.dataForm.coldProductivity.$touch()"
              :placeholder="$t('coldProductivity')"
              type="number"
            />
            <ValidationAlert
              v-if="($v.dataForm.coldProductivity.$dirty && !$v.dataForm.coldProductivity.numeric)"
              :text="$t('onlyNumeric')"
            />
          </div>
          <div class="col-3">
            <label>
              {{ $t('elEquipmentPower') }}
            </label>
            <b-input
              v-model="dataForm.elEquipmentPower"
              @blur="$v.dataForm.elEquipmentPower.$touch()"
              :placeholder="$t('elEquipmentPower')"
              type="number"
            />
            <ValidationAlert
              v-if="($v.dataForm.elEquipmentPower.$dirty && !$v.dataForm.elEquipmentPower.numeric)"
              :text="$t('onlyNumeric')"
            />
          </div>
        </div>

        <div class="flex-row-sb form-group mt-2">
          <div class="col-4">
            <label>
              {{ $t('typeGEU') }}
              <span class="required-field-star">*</span>
            </label>
            <multiselect
              v-model="dataForm.typeGEU"
              @close="$v.dataForm.typeGEU.$touch()"
              :options="mappingTypeGEU"
              :searchable="true"
              :placeholder="$t('typeGEU')"
              :label="labelName"
              track-by="id"
            />
            <ValidationAlert
              v-if="($v.dataForm.typeGEU.$dirty && !$v.dataForm.typeGEU.required)"
              :text="$t('emptyField')"
            />
          </div>
          <div class="col-4">
            <label>
              {{ $t('levelRefrigerantPlant') }}
            </label>
            <div class="flex-row-se">
              <b-form-checkbox
                v-model="dataForm.countLevelRefrigerPlant"
                name="levelRefrigerantPlant"
                value="1"
              >
                1
              </b-form-checkbox>
              <b-form-checkbox
                v-model="dataForm.countLevelRefrigerPlant"
                name="levelRefrigerantPlant"
                value="2"
              >
                2
              </b-form-checkbox>
            </div>
          </div>
          <div class="col-4">
            <label>
              {{ $t('apparatusGMZLB') }}
            </label>
            <div class="d-flex justify-content-center align-items-center">
              <b-form-checkbox
                v-model="dataForm.aparatusGMLZB"
                name="aparatusGMLZB"
                class="mx-1"
                switch
              />
              <div v-if="dataForm.aparatusGMLZB">
                {{ $t('present') }}
              </div>
              <div v-else>
                {{ $t('missingFemale') }}
              </div>
            </div>
          </div>
        </div>

        <div class="flex-row-sb form-group mt-2">
          <div class="col-6">
            <label>
              {{ $t('swimArea') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input
              v-model="dataForm.swimArea"
              @blur="$v.dataForm.swimArea.$touch()"
              :placeholder="$t('swimArea')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.swimArea.$dirty && !$v.dataForm.swimArea.required)"
              :text="$t('emptyField')"
            />
          </div>
          <div class="col-6">
            <label>
              {{ $t('swimPorts') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input
              v-model="dataForm.swimPorts"
              @blur="$v.dataForm.swimPorts.$touch()"
              :placeholder="$t('swimPorts')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.swimPorts.$dirty && !$v.dataForm.swimPorts.required)"
              :text="$t('emptyField')"
            />
          </div>
        </div>

        <h5 class="text-bold-600 mt-2">
          {{ $t('captain') }}:
        </h5>

        <div class="flex-row-sb form-group">
          <div class="col-12">
            <label>
              {{ $t('nameUK') }}
            </label>
            <b-input
              v-model="dataForm.nameCap"
              @blur="$v.dataForm.nameCap.$touch()"
              :placeholder="$t('lastNameUK')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.nameCap.$dirty && !$v.dataForm.nameCap.maxLength)"
              :text="$t('tooLongLastName')"
            />
            <ValidationAlert
              v-else-if="$v.dataForm.nameCap.$dirty && !$v.dataForm.nameCap.alphaUA"
              :text="$t('noAlphaUA')"
            />
          </div>
        </div>

        <div class="flex-row-sb form-group mt-2">
          <div class="col-6">
            <label>
              {{ $t('lastNameEN') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input
              v-model="dataForm.lastNameCapEN"
              @blur="$v.dataForm.lastNameCapEN.$touch()"
              :placeholder="$t('lastNameEN')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.lastNameCapEN.$dirty && !$v.dataForm.lastNameCapEN.required)"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.lastNameCapEN.$dirty && !$v.dataForm.lastNameCapEN.maxLength)"
              :text="$t('tooLongLastName')"
            />
            <ValidationAlert
              v-else-if="$v.dataForm.lastNameCapEN.$dirty && !$v.dataForm.lastNameCapEN.alphaEN"
              :text="$t('noAlpha')"
            />
          </div>
          <div class="col-6">
            <label>
              {{ $t('firstNameEN') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input
              v-model="dataForm.firstNameCapEN"
              @blur="$v.dataForm.firstNameCapEN.$touch()"
              :placeholder="$t('firstNameEN')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.firstNameCapEN.$dirty && !$v.dataForm.firstNameCapEN.required)"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.firstNameCapEN.$dirty && !$v.dataForm.firstNameCapEN.maxLength)"
              :text="$t('tooLongCaptName')"
            />
            <ValidationAlert
              v-else-if="$v.dataForm.firstNameCapEN.$dirty && !$v.dataForm.firstNameCapEN.alphaEN"
              :text="$t('noAlpha')"
            />
          </div>
        </div>

        <h5 class="text-bold-600 mt-2">
          {{ $t('experience') }}:
        </h5>

        <div class="flex-row-sb form-group">
          <div class="col-12">
            <label>
              {{ $t('bookPractical') }}
            </label>
            <div class="d-flex justify-content-start align-items-center">
              <b-form-checkbox
                v-model="dataForm.bookPractical"
                name="bookPractical"
                class="mx-1"
                switch
              />
              <div v-if="dataForm.bookPractical">
                {{ $t('present') }}
              </div>
              <div v-else>
                {{ $t('missingFemale') }}
              </div>
            </div>
          </div>
        </div>

        <div class="flex-row-sb form-group mt-2">
          <div class="col-6">
            <label>
              {{ $t('hirePlace') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input
              v-model="dataForm.hirePlace"
              @blur="$v.dataForm.hirePlace.$touch()"
              :placeholder="$t('hirePlace')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.hirePlace.$dirty && !$v.dataForm.hirePlace.required)"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.hirePlace.$dirty && !$v.dataForm.hirePlace.maxLength)"
              :text="$t('tooLongPlace')"
            />
          </div>
          <div class="col-6">
            <label>
              {{ $t('hireDate') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input-group>
              <b-form-input
                v-model="dataForm.hireDate"
                @blur="$v.hireDateObject.$touch()"
                type="date"
              />
              <b-input-group-append>
                <b-form-datepicker
                  v-model="dataForm.hireDate"
                  @hidden="$v.hireDateObject.$touch()"
                  :locale="lang"
                  :max="dataForm.fireDate || new Date()"
                  min="1900-01-01"
                  start-weekday="1"
                  button-only
                  right
                />
              </b-input-group-append>
            </b-input-group>
            <ValidationAlert
              v-if="($v.hireDateObject.$dirty && !$v.hireDateObject.required)"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="$v.hireDateObject.$dirty && (!$v.hireDateObject.minValue || !$v.hireDateObject.maxValue)"
              :text="$t('invalidDataFormat')"
            />
          </div>
        </div>

        <div class="flex-row-sb form-group mt-2">
          <div class="col-6">
            <label>
              {{ $t('firePlace') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input
              v-model="dataForm.firePlace"
              @blur="$v.dataForm.firePlace.$touch()"
              :placeholder="$t('firePlace')"
              type="text"
            />
            <ValidationAlert
              v-if="($v.dataForm.firePlace.$dirty && !$v.dataForm.firePlace.required)"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="($v.dataForm.firePlace.$dirty && !$v.dataForm.firePlace.maxLength)"
              :text="$t('tooLongPlace')"
            />
          </div>
          <div class="col-6">
            <label>
              {{ $t('fireDate') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input-group>
              <b-form-input
                v-model="dataForm.fireDate"
                @blur="$v.fireDateObject.$touch()"
                type="date"
              />
              <b-input-group-append>
                <b-form-datepicker
                  v-model="dataForm.fireDate"
                  @hidden="$v.fireDateObject.$touch()"
                  :locale="lang"
                  :min="dataForm.hireDate || '1900-01-01'"
                  :max="new Date()"
                  start-weekday="1"
                  button-only
                  right
                />
              </b-input-group-append>
            </b-input-group>
            <ValidationAlert
              v-if="($v.fireDateObject.$dirty && !$v.fireDateObject.required)"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="$v.fireDateObject.$dirty && (!$v.fireDateObject.minValue || !$v.fireDateObject.maxValue)"
              :text="$t('invalidDataFormat')"
            />
          </div>
        </div>

        <h5 class="text-bold-600 mt-2">
          {{ $t('repairedShip') }}:
        </h5>

        <div class="flex-row-sb form-group">
          <div class="col-12">
            <div class="d-flex justify-content-start align-items-center">
              <b-form-checkbox
                v-model="dataForm.repairedShip"
                name="bookPractical"
                class="mx-1"
                switch
              />
              <div v-if="dataForm.repairedShip">
                {{ $t('yes') }}
              </div>
              <div v-else>
                {{ $t('no') }}
              </div>
            </div>
          </div>
        </div>

        <div
          v-if="dataForm.repairedShip"
          class="col-12 d-flex"
        >
          <div class="col-4">
            <label>
              {{ $t('periodStart') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input-group>
              <b-form-input
                v-model="dataForm.repairedDateFrom"
                @input="displayDateInputs('repairing')"
                @blur="$v.repairedDateFromObject.$touch()"
                :readonly="dataForm.readonlyInputs"
                type="date"
              />
              <b-input-group-append>
                <b-form-datepicker
                  v-model="dataForm.repairedDateFrom"
                  @input="displayDateInputs('repairing')"
                  @hidden="$v.repairedDateFromObject.$touch()"
                  :disabled="dataForm.readonlyInputs"
                  :locale="lang"
                  :max="dataForm.repairedDateTo || dataForm.fireDate"
                  :min="dataForm.hireDate || '1900-01-01'"
                  start-weekday="1"
                  button-only
                  right
                />
              </b-input-group-append>
            </b-input-group>
            <ValidationAlert
              v-if="$v.repairedDateFromObject.$dirty && !$v.repairedDateFromObject.required"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="$v.repairedDateFromObject.$dirty && (!$v.repairedDateFromObject.minValue || !$v.repairedDateFromObject.maxValue)"
              :text="$t('invalidDataFormat')"
            />
          </div>
          <div class="col-4">
            <label>
              {{ $t('periodEnd') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input-group>
              <b-form-input
                v-model="dataForm.repairedDateTo"
                @input="displayDateInputs('repairing')"
                @blur="$v.repairedDateToObject.$touch()"
                :readonly="dataForm.readonlyInputs"
                type="date"
              />
              <b-input-group-append>
                <b-form-datepicker
                  v-model="dataForm.repairedDateTo"
                  @input="displayDateInputs('repairing')"
                  @hidden="$v.repairedDateToObject.$touch()"
                  :disabled="dataForm.readonlyInputs"
                  :locale="lang"
                  :max="dataForm.fireDate || new Date()"
                  :min="dataForm.repairedDateFrom || dataForm.hireDate"
                  start-weekday="1"
                  button-only
                  right
                />
              </b-input-group-append>
            </b-input-group>
            <ValidationAlert
              v-if="$v.repairedDateToObject.$dirty && !$v.repairedDateToObject.required"
              :text="$t('emptyField')"
            />
            <ValidationAlert
              v-else-if="$v.repairedDateToObject.$dirty && (!$v.repairedDateToObject.minValue || !$v.repairedDateToObject.maxValue)"
              :text="$t('invalidDataFormat')"
            />
          </div>
          <div class="col-1 d-flex justify-content-center align-items-center">
            <label>{{ $t('or') }}</label>
          </div>
          <div class="col-3">
            <label>
              {{ $t('totalDays') }}
              <span class="required-field-star">*</span>
            </label>
            <b-form-input
              v-model="dataForm.repairedTotalDays"
              @input="displayDateInputs('repairing')"
              @blur="$v.dataForm.repairedTotalDays.$touch()"
              :readonly="dataForm.readonlyDateNum"
              :placeholder="$t('totalDays')"
              type="number"
            />
            <ValidationAlert
              v-if="$v.dataForm.repairedTotalDays.$dirty && !$v.dataForm.repairedTotalDays.required"
              :text="$t('emptyField')"
            />
          </div>
        </div>

        <h5 class="text-bold-600 mt-2">
          {{ $t('responsibility') }}:
        </h5>

        <div class="flex-row-sb form-group">
          <div class="col-6">
            <label>
              {{ $t('responsibility') }}
            </label>
            <div class="d-flex">
              <multiselect
                v-model="dataForm.responsibility"
                @input="addResponsibility(dataForm.responsibility)"
                :options="mappingResponsibility"
                :searchable="true"
                :placeholder="$t('responsibility')"
                :label="labelName"
                track-by="id"
              />
              <unicon
                @click="addResponsibility(dataForm.responsibility)"
                name="plus"
                height="30px"
                width="30px"
                class="cursor add"
              />
            </div>
          </div>
          <div class="col-6">
            <label>
              {{ $t('positionOnShip') }}
              <span class="required-field-star">*</span>
            </label>
            <multiselect
              v-model="dataForm.positionOnShip"
              @close="$v.dataForm.positionOnShip.$touch()"
              :options="mappingPositionsShip"
              :searchable="true"
              :placeholder="$t('positionOnShip')"
              :label="labelName"
              track-by="id"
            />
            <ValidationAlert
              v-if="($v.dataForm.positionOnShip.$dirty && !$v.dataForm.positionOnShip.required)"
              :text="$t('emptyField')"
            />
          </div>
        </div>

        <div class="flex-row-sb form-group">
          <div class="col-12">
            <div
              v-for="(resp, index) in dataForm.responsibilityPeriods"
              :key="resp.id"
            >
              <div class="col-12 pl-0">
                <label>{{ resp[lang] }}:</label>
                <unicon
                  @click="deleteResponsibility(index)"
                  name="multiply"
                  fill="#42627e"
                  height="20px"
                  width="20px"
                  class="close"
                />
              </div>
              <div class="col-12 pl-0 pr-0 d-flex mb-1">
                <div class="col-4">
                  <label>
                    {{ $t('periodStart') }}
                    <span class="required-field-star">*</span>
                  </label>
                  <b-input-group>
                    <b-form-input
                      v-model="dataForm.responsibilityPeriods[index].date_from"
                      @input="displayDateInputs('responsibility')"
                      @blur="$v.dataForm.responsibilityPeriods.$each[index].date_from.$touch()"
                      :readonly="dataForm.readonlyInputs"
                      type="date"
                    />
                    <b-input-group-append>
                      <b-form-datepicker
                        v-model="dataForm.responsibilityPeriods[index].date_from"
                        @input="displayDateInputs('responsibility')"
                        @hidden="$v.dataForm.responsibilityPeriods.$each[index].date_from.$touch()"
                        :disabled="dataForm.readonlyInputs"
                        :locale="lang"
                        :max="dataForm.fireDate"
                        :min="dataForm.hireDate"
                        start-weekday="1"
                        button-only
                        right
                      />
                    </b-input-group-append>
                  </b-input-group>
                  <ValidationAlert
                    v-if="$v.dataForm.responsibilityPeriods.$each[index].date_from.$dirty &&
                      !$v.dataForm.responsibilityPeriods.$each[index].date_from.required"
                    :text="$t('emptyField')"
                  />
                </div>
                <div class="col-4">
                  <label>
                    {{ $t('periodEnd') }}
                    <span class="required-field-star">*</span>
                  </label>
                  <b-input-group>
                    <b-form-input
                      v-model="dataForm.responsibilityPeriods[index].date_to"
                      @input="displayDateInputs('responsibility')"
                      @blur="$v.dataForm.responsibilityPeriods.$each[index].date_to.$touch()"
                      :readonly="dataForm.readonlyInputs"
                      type="date"
                    />
                    <b-input-group-append>
                      <b-form-datepicker
                        v-model="dataForm.responsibilityPeriods[index].date_to"
                        @input="displayDateInputs('responsibility')"
                        @hidden="$v.dataForm.responsibilityPeriods.$each[index].date_to.$touch()"
                        :disabled="dataForm.readonlyInputs"
                        :locale="lang"
                        :max="dataForm.fireDate"
                        :min="dataForm.hireDate"
                        start-weekday="1"
                        button-only
                        right
                      />
                    </b-input-group-append>
                  </b-input-group>
                  <ValidationAlert
                    v-if="$v.dataForm.responsibilityPeriods.$each[index].date_to.$dirty &&
                      !$v.dataForm.responsibilityPeriods.$each[index].date_to.required"
                    :text="$t('emptyField')"
                  />
                </div>
                <div class="col-1 d-flex justify-content-center align-items-center">
                  <label>{{ $t('or') }}</label>
                </div>
                <div class="col-3">
                  <label>
                    {{ $t('totalDays') }}
                    <span class="required-field-star">*</span>
                  </label>
                  <b-form-input
                    v-model="dataForm.responsibilityPeriods[index].days_work"
                    @input="displayDateInputs('responsibility')"
                    @blur="$v.dataForm.responsibilityPeriods.$each[index].days_work.$touch()"
                    :readonly="dataForm.readonlyDateNum"
                    :placeholder="$t('totalDays')"
                    type="number"
                  />
                  <ValidationAlert
                    v-if="$v.dataForm.responsibilityPeriods.$each[index].days_work.$dirty &&
                      !$v.dataForm.responsibilityPeriods.$each[index].days_work.required"
                    :text="$t('emptyField')"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex-row-sb form-group mt-2">
          <div class="col-12">
            <label>
              {{ $t('numberPage') }}
              <span class="required-field-star">*</span>
            </label>
            <b-input
              v-model="dataForm.numberPageBook"
              @blur="$v.dataForm.numberPageBook.$touch()"
              :placeholder="$t('numberPage')"
              type="text"
            />
            <ValidationAlert
              v-if="$v.dataForm.numberPageBook.$dirty && !$v.dataForm.numberPageBook.required"
              :text="$t('emptyField')"
            />
          </div>
        </div>

        <div>
          <FileDropZone ref="mediaContent" class="w-100 p-0" />
        </div>
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
          type="submit"
          variant="success"
          class="mt-1"
        >
          {{ $t('save') }}
        </b-button>
      </b-overlay>
    </b-form>
  </b-card>
</template>

<script src="./SailorRecordBookLineAdd.js"/>
