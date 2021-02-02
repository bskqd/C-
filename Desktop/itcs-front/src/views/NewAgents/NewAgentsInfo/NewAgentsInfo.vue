<template>
  <div class="seafarerInfoList">
    <div class="w-33">
      <b>{{ $t('fullName') }}:</b>
      {{ sailorDocument.last_name }} {{ sailorDocument.first_name }} {{ sailorDocument.middle_name }}
    </div>
    <div class="w-33">
      <b>{{ $t('taxNumber') }}:</b>
      {{ sailorDocument.tax_number }}
    </div>
    <div class="w-33">
      <b>{{ $t('serialAndNum') }}:</b>
      {{ sailorDocument.serial_passport }}
    </div>
    <div class="w-50">
      <b>{{ $t('group') }}:</b>
      {{ sailorDocument.group.name_ukr }}
    </div>
    <div class="w-50">
      <b>{{ $t('city') }}:</b>
      {{ sailorDocument.city }}
    </div>
    <div class="w-50">
      <b>{{ $t('createDate') }}:</b>
      {{ sailorDocument.date_create }}
    </div>
    <div v-if="sailorDocument.contact_info.length">
      <div
        v-for="record of sailorDocument.contact_info"
        :key="record.id"
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
        {{ sailorDocument.status_document[labelName] }}
      </span>
    </div>
  </div>
</template>

<script src="./NewAgentsInfo.js" />
