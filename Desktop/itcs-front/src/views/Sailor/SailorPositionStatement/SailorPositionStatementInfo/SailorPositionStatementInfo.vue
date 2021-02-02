<template>
  <b-card header-tag="header">
    <div class="seafarerInfoList">
      <div class="w-100">
        <label class="text-bold-600">
          {{ $t('number') }}:
        </label>
        {{ sailorDocument.full_number }}
      </div>

        <div class="w-50">
          <label class="text-bold-600">
            {{ $t('rank') }}:
          </label>
          {{ sailorDocument.rank ? sailorDocument.rank[labelName] : $t('documentApplication') }}
        </div>

        <div
          v-if="sailorDocument.rank"
          class="w-50"
        >
          <label class="text-bold-600">
            {{ $t('position') }}:
          </label>
          <span v-for="position in sailorDocument.position" :key="position.id">
            {{ position[labelName] }};
          </span>
        </div>

      <div class="w-100">
        <label class="text-bold-600">
          {{ $t('payment') }}:
        </label>
        {{ sailorDocument.is_payed ? $t('isPayed') : $t('notPayed') }}
      </div>

      <div class="w-100">
        <label class="text-bold-600">
          {{ $t('price') }}:
        </label>
        {{ sailorDocument.price }} {{ $t('uah') }}
      </div>

      <div
        v-if="sailorIsCadet"
        class="w-100"
      >
        <label class="text-bold-600">
          {{ $t('educationWithSQC') }}:
        </label>
        {{ sailorDocument.education_with_sqc ? $t('yes') : $t('no') }}
      </div>

      <!----------------------------------------------------------------------------------->
      <div
        v-if="sailorDocument.dependencies.documents_and_statement.length"
        class="w-100"
      >
        <label class="text-bold-600">
          {{ $t('docs') }}:
        </label>
      </div>
      <b-table
        v-if="sailorDocument.dependencies.documents_and_statement.length"
        :items="sailorDocument.dependencies.documents_and_statement"
        :fields="existAndAfterDocsFields"
        :sort-by.sync="sortBy"
        :sort-desc.sync="sortDesc"
        striped
        hover
      >
        <template #cell(number)="row">
          <span v-if="row.item.get_info_for_statement">
            {{ row.item.get_info_for_statement.number }}
          </span>
        </template>

        <template #cell(name_issued)="row">
          <span v-if="row.item.get_info_for_statement">
            {{ row.item.get_info_for_statement.name_issued }}
          </span>
        </template>

        <template #cell(date_start)="row">
          <span v-if="row.item.get_info_for_statement">
            {{ getDateFormat(row.item.get_info_for_statement.date_start) }}
          </span>
        </template>

        <template #cell(date_end)="row">
          <span v-if="row.item.get_info_for_statement && row.item.get_info_for_statement.date_end">
            {{ getDateFormat(row.item.get_info_for_statement.date_end) }}
          </span>
        </template>

        <template #cell(info)="row">
          <span v-if="row.item.get_info_for_statement">
            {{ row.item.get_info_for_statement.info }}
          </span>
        </template>

        <template #cell(payment_info)="row">
          <div v-if="row.item.payment_url && checkAccess('agent')">
            <span v-if="row.item.get_info_for_statement">
              {{ setPriceWithCommission(row.item.price) }} {{ $t('uah') }}
            </span>
            <b-button
              @click="createPayment(row.item.payment_url)"
              variant="primary"
              class="m-0"
            >
              {{ $t('pay') }}
            </b-button>
          </div>
          <div v-else-if="row.item.payment_info" class="text-left">
            <div>
              <span class="text-bold-600">
                {{ $t('appointment') }}:
              </span>
              {{ row.item.payment_info.payment_due }}
            </div>
            <div>
              <span class="text-bold-600">
                {{ $t('requisites') }}:
              </span>
              {{ row.item.payment_info.requisites }}
            </div>
            <div>
              <span class="text-bold-600">
                {{ $t('price') }}:
              </span>
              {{ row.item.payment_info.amount }}
            </div>
          </div>
          <span v-else>
            {{ $t('notRequirePayment') }}
          </span>

        </template>

        <template #cell(status)="row">
          <span :class="getStatus(row.item.status)">
            {{ $t(`status${row.item.status}`) }}
          </span>
          <br/>
          <b-button
            v-if="checkAccess('agent') && row.item.allowCreateDiploma"
            @click="createDiploma"
            variant="primary"
            class="m-1"
          >
            {{ $t('createDiploma') }}
          </b-button>
        </template>
      </b-table>

      <!----------------------------------------------------------------------------------->
      <div
        v-if="sailorDocument.dependencies.missing.length"
        class="w-100 mt-2"
      >
        <label class="text-bold-600">
          {{ $t('missingStatement') }}:
        </label>
      </div>
      <b-table
        v-if="sailorDocument.dependencies.missing.length"
        :items="sailorDocument.dependencies.missing"
        :fields="missingDocFields"
        :sort-by.sync="sortBy"
        :sort-desc.sync="sortDesc"
        striped
        hover
      >
        <template #cell(document_description)="row">
          <span v-if="row.item.get_info_for_statement">
            {{ row.item.get_info_for_statement.document_description }}
          </span>
        </template>

        <template #cell(standarts_text)="row">
          <span v-if="row.item.get_info_for_statement">
            {{ row.item.get_info_for_statement.standarts_text }}
          </span>
        </template>

        <template #cell(date_start_meeting)="row">
          <span v-if="row.item.date_meeting">
            {{ getDateFormat(row.item.date_meeting.date_start_meeting) }}
          </span>
        </template>

        <template #cell(date_end_meeting)="row">
          <span v-if="row.item.date_meeting">
            {{ getDateFormat(row.item.date_meeting.date_end_meeting) }}
          </span>
        </template>

        <template #cell(payment_info)="row">
          <div v-if="row.item.payment_url && checkAccess('agent')">
            <span v-if="row.item.get_info_for_statement">
              {{ setPriceWithCommission(row.item.price) }} {{ $t('uah') }}
            </span>
            <b-button
              @click="createPayment(row.item.payment_url)"
              variant="primary"
              class="m-0"
            >
              {{ $t('pay') }}
            </b-button>
          </div>
          <div v-else-if="row.item.payment_info" class="text-left">
            <div>
              <span class="text-bold-600">
                {{ $t('appointment') }}:
              </span>
              {{ row.item.payment_info.payment_due }}
            </div>
            <div>
              <span class="text-bold-600">
                {{ $t('requisites') }}:
              </span>
              {{ row.item.payment_info.requisites }}
            </div>
            <div>
              <span class="text-bold-600">
                {{ $t('price') }}:
              </span>
              {{ row.item.payment_info.amount }}
            </div>
          </div>
          <span v-else>
            {{ $t('notRequirePayment') }}
          </span>
        </template>
      </b-table>

      <!----------------------------------------------------------------------------------->
      <div
        v-if="sailorDocument.dependencies.agent_and_service.length"
        class="w-100 mt-2"
      >
        <label class="text-bold-600">
          {{ $t('other') }}:
        </label>
      </div>
      <b-table
        v-if="sailorDocument.dependencies.agent_and_service.length"
        :items="sailorDocument.dependencies.agent_and_service"
        :fields="agentAndServiceCenterFields"
        :sort-by.sync="sortBy"
        :sort-desc.sync="sortDesc"
        striped
        hover
      >
        <template #cell(name)="row">
          {{ row.item.get_info_for_statement.name }}
        </template>

        <template #cell(additional)="row">
          {{ row.item.get_info_for_statement.additional }}
        </template>

        <template #cell(price)="row">
          <div v-if="row.item.payment_url && checkAccess('agent')">
            <span v-if="row.item.get_info_for_statement">
              {{ setPriceWithCommission(row.item.price) }} {{ $t('uah') }}
            </span>
            <b-button
              @click="createPayment(row.item.payment_url)"
              variant="primary"
              class="m-0"
            >
              {{ $t('pay') }}
            </b-button>
          </div>
          <div v-else-if="row.item.payment_info" class="text-left">
            <div>
              <span class="text-bold-600">
                {{ $t('appointment') }}:
              </span>
              {{ row.item.payment_info.payment_due }}
            </div>
            <div>
              <span class="text-bold-600">
                {{ $t('requisites') }}:
              </span>
              {{ row.item.payment_info.requisites }}
            </div>
            <div>
              <span class="text-bold-600">
                {{ $t('price') }}:
              </span>
              {{ row.item.payment_info.amount }}
            </div>
          </div>
        </template>
      </b-table>
    </div>
  </b-card>
</template>

<script src="./SailorPositionStatementInfo.js" />
