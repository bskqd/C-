<template>
  <b-card header-tag="header">
    <div
      v-if="sailorDocument.type_document.id !== 3"
      class="seafarerInfoList"
    >
      <div>
        <div>
          <b>{{ $t('strictBlank')}}:</b>
        </div>
        <div class="mr-1">
          <span>
            {{ sailorDocument.strict_blank }}
          </span>
        </div>
        <div>
          <b-button
            @click="saveDocument"
            class="text-bold-600 mt-0"
          >
            {{ $t('saveDoc') }}
          </b-button>
        </div>
      </div>
    </div>
    <div class="seafarerInfoList text-left">
      <!--typeId = 16 - Підтвердження робочого диплому-->
      <div
        v-if="sailorDocument.type_document.id !== 16 && !sailorDocument.other_number"
      >
        <b>{{ $t('number') }}:</b>
        {{ sailorDocument.number_document }}
      </div>
      <div v-else-if="sailorDocument.other_number">
        <b>{{ $t('number') }}:</b>
        {{ sailorDocument.other_number }}
      </div>
      <div v-if="basedQualificationStatement" class="w-50">
        <b>{{ $t('onBasisOf', { number: basedQualificationStatement.number }) }}</b>
        <router-link :to="{ name: 'qualification-statements-info', params: { id: this.id, documentID: sailorDocument.statement }}">
          ({{ $t('openStatement') }})
        </router-link>
      </div>
      <div class="w-50 text-left">
        <b>{{ $t('typeDoc') }}:</b>
        {{ sailorDocument.type_document[labelName] }}
      </div>
      <div class="w-50">
        <b>{{ $t('port') }}:</b>
        {{ !sailorDocument.other_port ? sailorDocument.port[labelName] : sailorDocument.other_port }}
      </div>
      <div class="w-50">
        <b>{{ $t('rank') }}:</b>
        {{ sailorDocument.rank[labelName] }}
      </div>
      <div class="w-50">
        <b>{{ $t('position') }}:</b>
        <span v-for="position in sailorDocument.list_positions" :key="position.id">{{ position[labelName] }};</span>
      </div>
      <div
        v-if="sailorDocument.type_document.id === 16"
        class="text-left w-100 p-0"
      >
        <b class="w-100">{{ $t('limitation') }}:</b>
        <div
          v-for="limitation in sailorDocument.function_limitation"
          :key="limitation.function.id"
          class="mb-1 w-100"
        >
          {{ limitation.function[labelName] }}:
          <div
            v-for="limit in limitation.limitations"
            :key="limit.id"
          >
            - {{ limit[labelName] }};
          </div>
        </div>
      </div>
      <div
        v-if="checkAccess('document-author-view') && sailorDocument.created_by"
        class="w-50"
      >
        <b>{{ $t('recordAuthor') }}:</b>
        {{ sailorDocument.created_by.name}}
      </div>
      <div
        v-if="checkAccess('document-author-view') && sailorDocument.created_by"
        class="w-50"
      >
        <b>{{ $t('createDate') }}:</b>
        {{ sailorDocument.created_by.date }}
      </div>
      <div
        v-if="checkAccess('verification-author-view') && sailorDocument.verificated_by"
        class="w-50"
      >
        <b>{{ $t('verificationDate') }}:</b>
        {{ sailorDocument.verificated_by.name }}
      </div>
      <div
        v-if="checkAccess('verification-author-view') && sailorDocument.verificated_by"
        class="w-50"
      >
        <b>{{ $t('verifier') }}:</b>
        {{ sailorDocument.verificated_by.date }}
      </div>
      <div class="w-50">
        <b>{{ $t('dateIssue') }}:</b>
        {{ getDateFormat(sailorDocument.date_start) }}
      </div>
      <div
        v-if="sailorDocument.date_end"
        class="w-50"
      >
        <b>{{ $t('dateEnd') }}:</b>
        {{ getDateFormat(sailorDocument.date_end) }}
      </div>
      <div>
        <b>{{ $t('status') }}:</b>
        <span :class="getStatus(sailorDocument.status_document.id)">
          {{ sailorDocument.status_document[labelName] }}
        </span>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorQualificationInfo.js"/>
