<template>
  <b-form @submit.prevent="validateForm">
    <div class="col-12 form-group text-left">
      <label>
        {{ $t('qualification') }} - {{ $t('rank') }}
        <span class="required-field-star">*</span>
      </label>
      <multiselect
        v-model="dataForm.rank"
        @input="enterDoublePosition(dataForm.rank, dataForm.position) + checkExistProtocolSQC(dataForm.rank)"
        @close="$v.dataForm.rank.$touch()"
        :options="ranksList"
        :placeholder="$t('qualification') + ' - ' + $t('rank')"
        :label="labelName"
        track-by="id"
      />
      <ValidationAlert
        v-if="$v.dataForm.rank.$dirty && !$v.dataForm.rank.required"
        :text="$t('emptyField')"
      />
    </div>
    <div class="col-12 form-group text-left mt-2">
      <label>
        {{ $t('position') }}
        <span class="required-field-star">*</span>
      </label>
      <multiselect
        v-model="dataForm.position"
        @close="$v.dataForm.position.$touch()"
        @remove="removePosition"
        :options="mappingPositions(dataForm.rank)"
        :label="labelName"
        :placeholder="$t('position')"
        track-by="id"
        multiple
      >
        <span slot="noOptions">
          {{ $t('selectRank') }}
        </span>
      </multiselect>
      <ValidationAlert
        v-if="$v.dataForm.position.$dirty && !$v.dataForm.position.required"
        :text="$t('emptyField')"
      />
    </div>
    <div class="col-12 form-group text-left mt-2">
      <label>
        {{ $t('swimPorts') }}
        <span class="required-field-star">*</span>
      </label>
      <multiselect
        v-model="dataForm.ports"
        @close="$v.dataForm.ports.$touch()"
        :options="mappingPorts"
        :taggable="true"
        :searchable="true"
        :placeholder="$t('swimPorts')"
        :label="labelName"
        track-by="id"
      />
      <ValidationAlert
        v-if="$v.dataForm.ports.$dirty && !$v.dataForm.ports.required"
        :text="$t('emptyField')"
      />
    </div>

    <div
      v-if="protocolView"
      class="col-12 form-group text-left mt-2"
    >
      <label>
        {{ $t('protocolSQC') }}
        <span class="required-field-star">*</span>
      </label>
      <multiselect
        v-model="dataForm.protocol"
        @close="$v.dataForm.protocol.$touch()"
        :options="dataForm.protocolsList"
        :label="labelName"
        :placeholder="$t('protocolSQC')"
        track-by="id"
      >
        <span slot="noOptions">
          {{ $t('notFind') }}
        </span>
      </multiselect>
      <ValidationAlert
        v-if="$v.dataForm.protocol.$dirty && !$v.dataForm.protocol.required"
        :text="$t('emptyField')"
      />
    </div>
    <div
      v-if="typeView"
      class="col-12 form-group text-left mt-2"
    >
      <label>
        {{ $t('type') }}
        <span class="required-field-star">*</span>
      </label>
      <multiselect
        v-model="dataForm.type"
        @input="checkExistProtocolSQC(dataForm.rank)"
        @close="$v.dataForm.type.$touch()"
        :options="dataForm.typeList"
        :taggable="true"
        :searchable="true"
        :placeholder="$t('type')"
        :label="labelName"
        track-by="id"
      />
      <ValidationAlert
        v-if="$v.dataForm.type.$dirty && !$v.dataForm.type.required"
        :text="$t('emptyField')"
      />
    </div>
    <div>
      <FileDropZone ref="mediaContent" class="w-100" />
    </div>
    <b-overlay
      :show="dataForm.buttonLoader"
      spinner-variant="primary"
      opacity="0.65"
      blur="2px"
      variant="white"
      class="w-100 mt-1"
      spinner-small
    >
      <b-button
        type="submit"
        variant="success"
      >
        {{ $t('save') }}
      </b-button>
    </b-overlay>
  </b-form>
</template>

<script src="./SailorQualificationStatementAdd.js"/>
