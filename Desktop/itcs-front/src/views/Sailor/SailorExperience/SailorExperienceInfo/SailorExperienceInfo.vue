<template>
  <b-card header-tag="header">
    <div
      v-if="sailorDocument.record_type === 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'"
      class="seafarerInfoList parrentMb-0"
    >
      <div class="w-100">
        <b>{{ $t('typeDoc') }}:</b>
        {{ sailorDocument.record_type }}
      </div>
      <div class="w-100 p-0 text-left">
        <b class="w-100">{{ $t('responsibility') }}:</b>
        <span class="w-100">{{ sailorDocument.responsibility_work_book[labelName] }}</span>
        <span v-if="sailorDocument.date_start" class="w-33">
          {{ $t('periodStart') }}: {{ getDateFormat(sailorDocument.date_start) }}
        </span>
        <span v-if="sailorDocument.date_end" class="w-33">
          {{ $t('periodEnd') }}: {{ getDateFormat(sailorDocument.date_end) }}
        </span>
        <span v-if="sailorDocument.days_work" class="w-33">
          {{ $t('totalDays') }}: {{ sailorDocument.days_work }}
        </span>
      </div>
      <div class="w-100">
        <b>{{ $t('workPlace') }}:</b>
        {{ sailorDocument.place_work }}
      </div>
      <div>
        <b>{{ $t('bookPractical') }}:</b>
        {{ sailorDocument.book_registration_practical ? $t('present') : $t('missingFemale') }}
      </div>
      <div
        v-if="checkAccess('document-author-view')"
        class="seafarerInfoList p-0"
      >
        <div class="w-50">
          <b>{{ $t('recordAuthor') }}:</b>
          {{ sailorDocument.created_by.name }}
        </div>
        <div class="w-50">
          <b>{{ $t('createDate') }}:</b>
          {{ sailorDocument.created_by.date }}
        </div>
      </div>
      <div
        v-if="checkAccess('verification-author-view') && sailorDocument.verificated_by"
        class="seafarerInfoList p-0"
      >
        <div class="w-50">
          <b>{{ $t('verifier') }}:</b>
          {{ sailorDocument.verificated_by.name }}
        </div>
        <div class="w-50">
          <b>{{ $t('verificationDate') }}:</b>
          {{ sailorDocument.verificated_by.date }}
        </div>
      </div>
      <div class="w-50">
        <b>{{ $t('status') }}:</b>
        <span :class="getStatus(sailorDocument.status_line.id)">
        {{ sailorDocument.status_line[labelName] }}
      </span>
      </div>
    </div>
    <div
      v-else
      class="seafarerInfoList parrentMb-0"
    >
      <div>
        <h5 class="text-bold-600 ml-0 pl-0">
          {{ $t('mainInfo') }}:
        </h5>
      </div>
      <div class="w-100">
        <b>{{ $t('typeDoc') }}:</b>
        {{ sailorDocument.record_type }}
      </div>
      <div class="w-50">
        <b>{{ $t('captain') }}:</b>
        {{ sailorDocument.full_name_master }}
      </div>
      <div class="w-50">
        <b>{{ $t('captainEng') }}:</b>
        {{ sailorDocument.full_name_master_eng }}
      </div>
      <div class="w-50">
        <b>{{ $t('ownerShip') }}:</b>
        {{ sailorDocument.ship_owner }}
      </div>
      <div class="w-50">
        <b>{{ $t('nameShip') }}:</b>
        {{ sailorDocument.name_vessel }}
      </div>
      <div class="w-50">
        <b>{{ $t('numShip') }}:</b>
        {{ sailorDocument.number_vessel }}
      </div>
      <div class="w-50">
        <b>{{ $t('typeShip') }}:</b>
        {{ sailorDocument.type_vessel[labelName] }}
      </div>
      <div class="w-50">
        <b>{{ $t('portShip') }}:</b>
        {{ sailorDocument.port_of_registration }}
      </div>
      <div class="w-50">
        <b>{{ $t('modeShipping') }}:</b>
        {{ sailorDocument.mode_of_navigation[labelName] }}
      </div>
      <div>
        <h5 class="text-bold-600 ml-0 pl-0 mt-1">
          {{ $t('ttx') }}:
        </h5>
      </div>
      <div class="w-50">
        <b>{{ $t('grossCapacity') }}:</b>
        {{ sailorDocument.gross_capacity }}
      </div>
      <div class="w-50">
        <b>{{ $t('typeGEU') }}:</b>
        {{ sailorDocument.type_geu[labelName] }}
      </div>
      <div class="w-50">
        <b>{{ $t('powerGEU') }}:</b>
        {{ sailorDocument.propulsion_power }}
      </div>
      <div class="w-50">
        <b>{{ $t('levelRefrigerantPlant') }}:</b>
        {{ sailorDocument.levelRefrigerPlant }}
      </div>

      <div class="w-50">
        <b>{{ $t('coldProductivity') }}:</b>
        {{ sailorDocument.refrigerating_power }}
      </div>
      <div class="w-50">
        <b>{{ $t('elEquipmentPower') }}:</b>
        {{ sailorDocument.electrical_power }}
      </div>
      <div class="w-50">
        <b>{{ $t('apparatusGMZLB') }}:</b>
        {{ sailorDocument.equipment_gmzlb ? $t('present') : $t('missingFemale') }}
      </div>
      <div>
        <h5 class="text-bold-600 ml-0 pl-0 mt-1">
          {{ $t('port') }}:
        </h5>
      </div>
      <div class="w-50">
        <b>{{ $t('swimArea') }}:</b>
        {{ sailorDocument.trading_area }}
      </div>
      <div class="w-50">
        <b>{{ $t('swimPorts') }}:</b>
        {{ sailorDocument.ports_input }}
      </div>
      <div>
        <h5 class="text-bold-600 ml-0 pl-0 mt-1">
          {{ $t('employment') }}:
        </h5>
      </div>
      <div class="w-50">
        <b>{{ $t('positionOnShip') }}:</b>
        {{ sailorDocument.position[labelName] }}
      </div>
      <div v-if="sailorDocument.all_responsibility.length" class="text-left">
        <b class="w-100">{{ $t('responsibility') }}:</b>
        <div
          v-for="resp of sailorDocument.all_responsibility"
          :key="resp.id"
        >
          <p v-if="resp.responsibility">
            <span class="w-100">
              {{ resp.responsibility[labelName] }}
            </span><br/>
            <span v-if="resp.date_from" class="w-33">
              {{ $t('periodStart') }}: {{ getDateFormat(resp.date_from) }}
            </span>
            <span v-if="resp.date_to" class="w-33">
              {{ $t('periodEnd') }}: {{ getDateFormat(resp.date_to) }}
            </span>
            <span v-if="resp.days_work" class="w-33">
              {{ $t('totalDays') }}: {{ resp.days_work }}
            </span>
          </p>
        </div>
      </div>
      <div>
        <b>{{ $t('repairedShip') }}:</b>
        {{ sailorDocument.is_repaired ? $t('yes') : $t('no') }}
      </div>
      <div v-if="sailorDocument.is_repaired" class="w-100 text-left">
        <span v-if="sailorDocument.repair_date_from" class="w-33">
          {{ $t('periodStart') }}: {{ getDateFormat(sailorDocument.repair_date_from) }}
        </span>
        <span v-if="sailorDocument.repair_date_to" class="w-33">
          {{ $t('periodEnd') }}: {{ getDateFormat(sailorDocument.repair_date_to) }}
        </span>
        <span v-if="sailorDocument.days_repair" class="w-33">
          {{ $t('totalDays') }}: {{ sailorDocument.days_repair }}
        </span>
      </div>
      <div class="w-50">
        <b>{{ $t('hirePlace') }}:</b>
        {{ sailorDocument.place_start }}
      </div>
      <div class="w-50">
        <b>{{ $t('firePlace') }}:</b>
        {{ sailorDocument.place_end }}
      </div>
      <div class="w-50">
        <b>{{ $t('hireDate') }}:</b>
        {{ getDateFormat(sailorDocument.date_start) }}
      </div>
      <div class="w-50">
        <b>{{ $t('fireDate') }}:</b>
        {{ getDateFormat(sailorDocument.date_end) }}
      </div>
      <div>
        <b>{{ $t('bookPractical') }}:</b>
        {{ sailorDocument.book_registration_practical ? $t('present') : $t('missingFemale') }}
      </div>
      <div
        v-if="checkAccess('document-author-view')"
        class="seafarerInfoList p-0"
      >
        <div class="w-50">
          <b>{{ $t('recordAuthor') }}:</b>
          {{ sailorDocument.created_by.name }}
        </div>
        <div class="w-50">
          <b>{{ $t('createDate') }}:</b>
          {{ sailorDocument.created_by.date }}
        </div>
      </div>
      <div
        v-if="checkAccess('verification-author-view') && sailorDocument.verificated_by"
        class="seafarerInfoList p-0"
      >
        <div class="w-50">
          <b>{{ $t('verifier') }}:</b>
          {{ sailorDocument.verificated_by.name }}
        </div>
        <div class="w-50">
          <b>{{ $t('verificationDate') }}:</b>
          {{ sailorDocument.verificated_by.date}}
        </div>
      </div>
      <div class="w-50">
        <b>{{ $t('status') }}:</b>
        <span :class="getStatus(sailorDocument.status_line.id)">
        {{ sailorDocument.status_line[labelName] }}
      </span>
      </div>
    </div>
  </b-card>
</template>

<script src="./SailorExperienceInfo.js"/>
