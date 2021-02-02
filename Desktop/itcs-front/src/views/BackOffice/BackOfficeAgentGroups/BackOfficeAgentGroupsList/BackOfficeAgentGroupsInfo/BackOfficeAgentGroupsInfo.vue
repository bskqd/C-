<template>
  <b-card header-tag="header">
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase">
          {{ $t('agentInfo') }}
        </div>
        <unicon
          @click="hideDetailed(row)"
          name="multiply"
          fill="#42627e"
          height="20px"
          width="20px"
          class="close"
        />
      </div>
    </template>
    <div class="seafarerInfoList">
      <div class="w-33">
        <b>{{ $t('agentFullName')}}:</b>
        {{ row.item.agentFullName }}
      </div>
      <div class="w-33">
        <b>{{ $t('agentGroup')}}:</b>
        <span
          v-for="record of row.item.agent_group"
          :key="record.id"
          class="mr-1"
        >
          {{ record.name_ukr }};
        </span>
      </div>
      <div class="w-33">
        <b>{{ $t('position')}}:</b>
        {{ row.item.userType }}
      </div>
      <div class="w-50">
        <b>{{ $t('affiliate')}}:</b>
        {{ row.item.userprofile.branch_office }}
      </div>
      <div class="w-50">
        <b>{{ $t('city')}}:</b>
        {{ row.item.userprofile.city }}
      </div>
      <div
        v-if="row.item.userprofile.contact_info.length"
        class="w-100 pl-1 pr-1"
      >
        <div
          v-for="record of row.item.userprofile.contact_info"
          :key="record.id"
          class="w-25 text-left p-0"
        >
          <span v-if="record.type_contact === '1' || record.type_contact === 'phone_number'">
            <b>{{ $t('phoneNumber') }}:</b>
            {{ record.value }}
          </span>
          <span v-else-if="record.type_contact === '4' || record.type_contact === 'telegram'">
            <b>Telegram:</b>
            {{ record.value }}
          </span>
          <span v-else-if="record.type_contact === '5' || record.type_contact === 'viber'">
            <b>Viber:</b>
            {{ record.value }}
          </span>
          <span v-else-if="record.type_contact === '2' || record.type_contact === 'email'">
            <b>{{ $t('email') }}:</b>
            {{ record.value }}
          </span>
        </div>
      </div>
    </div>
  </b-card>
</template>

<script src="./BackOfficeAgentGroupsInfo.js" />
