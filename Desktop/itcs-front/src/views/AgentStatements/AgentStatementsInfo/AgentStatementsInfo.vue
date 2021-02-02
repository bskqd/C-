<template>
  <b-card
    header-tag="header"
    class="pb-2"
  >
    <div class="seafarerInfoList">
      <div>
        <b>{{ $t('sailorFullName') }}:</b>
        {{ sailorDocument.seafarerFullName }}
      </div>
      <div v-if="checkAccess('agentStatements', 'showAgentName')">
        <b>{{ $t('agentFullName') }}:</b>
        {{ sailorDocument.agentFullName }}
      </div>
      <div>
        <b>{{ $t('city') }}:</b>
        {{ sailorDocument.city }}
      </div>
      <div class="w-50">
        <b>{{ $t('contractDateEnd') }}:</b>
        {{ getDateFormat(sailorDocument.date_end_proxy) }}
      </div>
      <div class="w-50">
        <b>{{ $t('createDate') }}:</b>
        {{ sailorDocument.date_create }}
      </div>
      <div class="w-50">
        <b>{{ $t('dateModified') }}:</b>
        {{ sailorDocument.date_modified }}
      </div>
      <div v-if="sailorDocument.agent.userprofile.contact_info.length">
        <div
          v-for="(record, index) of sailorDocument.agent.userprofile.contact_info"
          :key="index"
          class="w-25 text-left p-0"
        >
          <span v-if="record.type_contact === 'phone_number' || record.type_contact === '1'">
            <b>{{ $t('phoneNumber') }}:</b>
            {{ record.value }}
          </span>
          <span v-else-if="record.type_contact === 'telegram' || record.type_contact === '4'">
            <b>Telegram:</b>
            {{ record.value }}
          </span>
          <span v-else-if="record.type_contact === 'viber' || record.type_contact === '5'">
            <b>Viber:</b>
            {{ record.value }}
          </span>
          <span v-else-if="record.type_contact === 'email' || record.type_contact === '2'">
            <b>{{ $t('email') }}:</b>
            {{ record.value }}
          </span>
        </div>
      </div>
      <div>
        <b>{{ $t('status') }}:</b>
        <span :class="getStatus(sailorDocument.status_document.id)">
          {{ sailorDocument.status_document[langFields] }}
        </span>
      </div>
    </div>
  </b-card>
</template>

<script src="./AgentStatementsInfo.js" />
