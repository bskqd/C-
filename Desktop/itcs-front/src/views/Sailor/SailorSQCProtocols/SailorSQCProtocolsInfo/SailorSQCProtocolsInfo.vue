<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList text-left">
      <div class="d-flex">
        <div v-if="sailorDocument.is_printeble && sailorDocument.decision" class="mr-3">
          <b-button
            @click="saveDocument()"
            class="text-bold-600"
          >
            {{ $t('saveProtocol') }}
          </b-button>
        </div>

        <div v-if="checkAccess('sailorSQCProtocols', 'regeneration', sailorDocument)" class="mr-3">
          <b-button
            @click="regenerateProtocol()"
            class="text-bold-600"
          >
            {{ $t('regenerateDoc') }}
          </b-button>
        </div>

        <div v-if="sailorDocument.downloadable_with_sign && sailorDocument.decision">
          <b-button
            @click="saveDocWithSign()"
            class="text-bold-600"
          >
            {{ $t('saveDocWithSign') }}
          </b-button>
        </div>
      </div>

      <!--<div
        v-if="checkAccess('sailorSQCProtocols', 'signature', sailorDocument)"
        class="w-100 ml-1"
      >
        <Signature
          ref="signature"
          :signAccess="sailorDocument.signing.sign_access"
          :protocolData="sailorDocument"
        />
      </div>-->

      <div class="w-50">
        <label class="text-bold-600">
          {{ $t('number') }}:
        </label>
        {{ sailorDocument.number_document }}
      </div>

      <div v-if="basedStatementSQC" class="w-50">
        <label class="text-bold-600">
          {{ $t('onBasisOf', { number: basedStatementSQC.number }) }}
        </label>
        <router-link :to="{ name: 'sqc-statements-info', params: { documentID: sailorDocument.statement_dkk }}">
          ({{ $t('openStatement') }})
        </router-link>
      </div>

      <div class="w-50">
        <label class="text-bold-600">
          {{ $t('dataEvent') }}:
        </label>
        {{ getDateFormat(sailorDocument.date_meeting) }}
      </div>

      <div class="w-50">
        <label class="text-bold-600">
          {{ $t('rank') }}:
        </label>
        {{ sailorDocument.rank[labelName] }}
      </div>

      <div class="w-50">
        <label class="text-bold-600">
          {{ $t('position') }}:
        </label>
        <span v-for="position in sailorDocument.position" :key="position.id">
          {{ position[labelName] }};
        </span>
      </div>

      <div class="w-50">
        <label class="text-bold-600">
          {{ $t('headCommission') }}:
        </label>
        {{ sailorDocument.headCommission.user_fio_ukr }}
      </div>

      <div class="w-50">
        <label class="text-bold-600">
          {{ $t('secretaryCommission') }}:
        </label>
        {{ sailorDocument.secretaryCommission.user_fio_ukr }}
      </div>

      <div class="w-50">
        <label class="text-bold-600">
          {{ $t('membersCommission') }}:
        </label>
        <span
          v-for="(member, index) in sailorDocument.membersCommission"
          :key="index"
        >
          {{ member.user_fio_ukr }};
        </span>
      </div>

      <div
        v-if="checkAccess('document-author-view') && sailorDocument.created_by"
        class="w-100 p-0 d-flex"
      >
        <div class="w-50">
          <label class="text-bold-600">
            {{ $t('recordAuthor') }}:
          </label>
          {{ sailorDocument.created_by.name }}
        </div>
        <div class="w-50">
          <label class="text-bold-600">
            {{ $t('createDate') }}:
          </label>
          {{ sailorDocument.created_by.date }}
        </div>
      </div>

      <div class="w-100">
        <label class="text-bold-600 mr-1">
          {{ $t('status') }}:
        </label>
        <span :class="getStatus(sailorDocument.status_document.id)">
          {{ sailorDocument.status_document[labelName] }}
        </span>
      </div>

      <div class="w-100">
        <label class="text-bold-600 mr-1">
          {{ $t('solution') }}:
        </label>
        <span :class="getStatus(sailorDocument.decision ? sailorDocument.decision.id : 5)">
          {{ sailorDocument.decision ? sailorDocument.decision[labelName]: $t('waitForDecision') }}
        </span>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorSQCProtocolsInfo.js" />
