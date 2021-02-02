<template>
  <b-card header-tag="header">
    <template #header>
      <div class="flex-row-sb">
        <div class="text-uppercase">
          {{ $t('userDocChanges') }}
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
    <div class="seafarerInfoList text-left">
      <div v-if="!row.item.new_obj_json">
        <span class="deleted-record">
          {{ $t('deletedDocument') }}
        </span>
      </div>
      <div v-else-if="Object.keys(row.item.new_obj_json).length === 1">
        <span class="expired-record">
          {{ $t('expiredDocument') }}
        </span>
      </div>
      <div v-else>
        <div v-if="!row.item.old_obj_json" class="w-100 pl-1 pr-1 mb-1">
          <span class="added-record m-0">
            {{ $t('addedDocument') }}
          </span>
        </div>
        <ChangedField
          v-if="row.item.content_type === 'sailorpassport' || row.item.content_type === 'passport' ||
           row.item.content_type === 'city'"
          :row="row"
          :newValue="row.item.new_obj_json.country[langCountry]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.country[langCountry] : null"
          labelName="country"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'city'"
          :row="row"
          :newValue="row.item.new_obj_json.region[langCountry]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.region[langCountry] : null"
          labelName="region"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'city'"
          :row="row"
          :newValue="row.item.new_obj_json.value"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.value : null"
          labelName="nameUa"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'city'"
          :row="row"
          :newValue="row.item.new_obj_json.value_eng"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.value_eng : null"
          labelName="nameEn"
          class="w-50"
        />
        <div
          v-if="row.item.content_type === 'sailorpassport' || row.item.content_type === 'statementsailorpassport' ||
           row.item.content_type === 'qualitifcationdocument' || row.item.content_type === 'proofofworkdiploma' ||
           row.item.content_type === 'statemenetqualificationdocument' || row.item.content_type === 'qualificationdocument'"
          class="w-50"
        >
          <ChangedField
            v-if="row.item.new_obj_json.port"
            :row="row"
            :newValue="row.item.new_obj_json.port[langFields]"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.port[langFields] : null"
            labelName="port"
          />
          <ChangedField
            v-else
            :row="row"
            :newValue="row.item.new_obj_json.other_port"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.other_port : null"
            labelName="port"
          />
        </div>
        <ChangedField
          v-if="row.item.content_type === 'sailorpassport' || row.item.content_type === 'education' ||
           ((row.item.content_type === 'qualitifcationdocument' || row.item.content_type === 'qualificationdocument') &&
           row.item.new_obj_json.type_document.id === 49) || row.item.content_type === 'proofofworkdiploma' ||
           row.item.content_type === 'protocolsqc'"
          :row="row"
          :newValue="row.item.new_obj_json.number_document"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.number_document : null"
          labelName="number"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statementsailorpassport' || row.item.content_type === 'studentid' ||
           row.item.content_type === 'statementadvancedtraining' || ((row.item.content_type === 'qualitifcationdocument' ||
           row.item.content_type === 'qualificationdocument') && row.item.new_obj_json.type_document.id !== 49) ||
           row.item.content_type === 'statemenetqualificationdocument' || row.item.content_type === 'statementeti' ||
           row.item.content_type === 'sailorstatementdkk' || row.item.content_type === 'medicalsertificate' ||
           row.item.content_type === 'statementmedicalcertificate' || row.item.content_type === 'medicalcertificate' ||
           row.item.content_type === 'statementsqc'"
          :row="row"
          :newValue="row.item.new_obj_json.number"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.number : null"
          labelName="number"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'education'"
          :row="row"
          :newValue="row.item.new_obj_json.registry_number"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.registry_number : null"
          labelName="registrationNumber"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'certificateeti'"
          :row="row"
          :newValue="row.item.new_obj_json.ntz_number"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.ntz_number : null"
          labelName="number"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'packetitem'"
          :row="row"
          :newValue="row.item.new_obj_json.full_number"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.full_number : null"
          labelName="number"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'etiregistry'"
          :row="row"
          :newValue="row.item.new_obj_json.full_number_protocol"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.full_number_protocol : null"
          labelName="numberProtocol"
          class="w-50"
        />
        <div
          v-if="row.item.content_type === 'lineinservicerecord' && (!row.item.new_obj_json.record_type ||
           row.item.new_obj_json.record_type === 'Довідка про стаж плавання')"
          class="d-flex wrap"
        >
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.number_vessel"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.number_vessel : null"
            labelName="numShip"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.name_vessel"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.name_vessel : null"
            labelName="nameShip"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.type_vessel[langFields]"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.type_vessel[langFields] : null"
            labelName="typeShip"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.mode_of_navigation[langFields]"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.mode_of_navigation[langFields] : null"
            labelName="modeShipping"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.port_of_registration"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.port_of_registration : null"
            labelName="portShip"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.ship_owner"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.ship_owner : null"
            labelName="ownerShip"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.gross_capacity"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.gross_capacity : null"
            labelName="grossCapacity"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.propulsion_power"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.propulsion_power : null"
            labelName="powerGEU"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.refrigerating_power"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.refrigerating_power : null"
            labelName="coldProductivity"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.electrical_power"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.electrical_power : null"
            labelName="elEquipmentPower"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.type_geu[langFields]"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.type_geu[langFields] : null"
            labelName="typeGEU"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.levelRefrigerPlant"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.levelRefrigerPlant : null"
            labelName="levelRefrigerantPlant"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.equipment_gmzlb ? this.$i18n.t('present') : this.$i18n.t('missingFemale')"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.equipment_gmzlb ? $t('present') : $t('missingFemale') : null"
            labelName="apparatusGMZLB"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.trading_area"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.trading_area : null"
            labelName="swimArea"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.ports_input"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.ports_input : null"
            labelName="swimPorts"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.full_name_master"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.full_name_master : null"
            labelName="nameUK"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.full_name_master_eng"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.full_name_master_eng : null"
            labelName="nameEN"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.place_start"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.place_start : null"
            labelName="hirePlace"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.place_end"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.place_end : null"
            labelName="firePlace"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.is_repaired ? this.$i18n.t('yes') : this.$i18n.t('no')"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.is_repaired ? $t('yes') : $t('no') : null"
            labelName="repairedShip"
            class="w-50"
          />
          <ChangedField
            v-if="row.item.new_obj_json.is_repaired"
            :row="row"
            :newValue="dateNewValue('repair_date_from')"
            :oldValue="dateOldValue('repair_date_from')"
            labelName="periodStart"
            class="w-33"
          />
          <ChangedField
            v-if="row.item.new_obj_json.is_repaired"
            :row="row"
            :newValue="dateNewValue('repair_date_to')"
            :oldValue="dateOldValue('repair_date_to')"
            labelName="periodEnd"
            class="w-33"
          />
          <ChangedField
            v-if="row.item.new_obj_json.is_repaired"
            :row="row"
            :newValue="row.item.new_obj_json.days_repair"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.days_repair : null"
            labelName="totalDays"
            class="w-33"
          />
          <div class="w-100 pl-1 pr-1">
            <div v-if="!row.item.old_obj_json">
              <label>{{ $t('responsibility') }}:</label>
              <div
                v-for="(responsibility, index) of row.item.new_obj_json.all_responsibility"
                :key="index"
                class="mb-1"
              >
                <div v-if="responsibility.responsibility">
                  <div>{{ responsibility.responsibility[langFields] }}:</div>
                  <div>
                    <span v-if="responsibility.date_from">{{ $t('periodStart') }}: {{ getDateFormat(responsibility.date_from) }}; </span>
                    <span v-if="responsibility.date_to">{{ $t('periodEnd') }}: {{ getDateFormat(responsibility.date_to) }}; </span>
                    <span v-else>{{ $t('totalDays') }}: {{ responsibility.days_work }};</span>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="mb-1">
              <label>{{ $t('responsibility') }}:</label>
              <div
                v-for="responsibility of this.arrayDifference"
                :key="responsibility.id"
                :class="{
                  'added-record mb-1': responsibility.status === 'added',
                  'deleted-record mb-1': responsibility.status === 'deleted',
                  'exist-record mb-1': responsibility.status === 'exists'
                }"
              >
                <div>{{ responsibility.name }}:</div>
                <div>
                  <span v-if="responsibility.dateFrom">{{ $t('periodStart') }}: {{ responsibility.dateFrom }}; </span>
                  <span v-if="responsibility.dateTo">{{ $t('periodEnd') }}: {{ responsibility.dateTo }}; </span>
                  <span v-else>{{ $t('totalDays') }}: {{ responsibility.totalDays }};</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <ChangedField
          v-if="row.item.content_type === 'lineinservicerecord'"
          :row="row"
          :newValue="row.item.new_obj_json.book_registration_practical ? $t('present') : $t('missingFemale')"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.book_registration_practical ? $t('present') : $t('missingFemale') : null"
          labelName="bookPractical"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'lineinservicerecord' && row.item.new_obj_json.record_type === 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'"
          :row="row"
          :newValue="row.item.new_obj_json.place_work"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.place_work : null"
          labelName="workPlace"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'lineinservicerecord' && row.item.new_obj_json.record_type === 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'"
          :row="row"
          :newValue="row.item.new_obj_json.responsibility_work_book[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.responsibility_work_book[langFields] : null"
          labelName="responsibility"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'servicerecord'"
          :row="row"
          :newValue="row.item.new_obj_json.name_book"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.name_book : null"
          labelName="number"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statemenetqualificationdocument'"
          :row="row"
          :newValue="row.item.new_obj_json.protocol_dkk ? row.item.new_obj_json.protocol_dkk.number: null"
          :oldValue="row.item.old_obj_json && row.item.old_obj_json.protocol_dkk ? row.item.old_obj_json.protocol_dkk.number : null"
          labelName="numberProtocol"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'passport' || row.item.content_type === 'education' ||
           row.item.content_type === 'studentid'"
          :row="row"
          :newValue="row.item.new_obj_json.serial"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.serial : null"
          labelName="serial"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'studentid'"
          :row="row"
          :newValue="row.item.new_obj_json.group"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.group : null"
          labelName="group"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'education' || row.item.content_type === 'qualitifcationdocument'||
           row.item.content_type === 'qualificationdocument' || row.item.content_type === 'proofofworkdiploma' ||
           row.item.content_type === 'statemenetqualificationdocument'"
          :row="row"
          :newValue="row.item.new_obj_json.type_document ? row.item.new_obj_json.type_document[langFields] : null"
          :oldValue="row.item.old_obj_json && row.item.old_obj_json.type_document ? row.item.old_obj_json.type_document[langFields] : null"
          labelName="typeDoc"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'servicerecord'"
          :row="row"
          :newValue="row.item.new_obj_json.branch_office[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.branch_office[langFields] : null"
          labelName="affiliate"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'packetitem'"
          :row="row"
          :newValue="row.item.new_obj_json.service_center[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.service_center[langFields] : null"
          labelName="affiliate"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'protocolsqc'"
          :row="row"
          :newValue="row.item.new_obj_json.branch_create[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.branch_create[langFields] : null"
          labelName="affiliate"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'education' || row.item.content_type === 'studentid'"
          :row="row"
          :newValue="row.item.new_obj_json.name_nz[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.name_nz[langFields] : null"
          labelName="nameInstitution"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statementadvancedtraining'"
          :row="row"
          :newValue="row.item.new_obj_json.educational_institution[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.educational_institution[langFields] : null"
          labelName="nameInstitution"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statementeti' || row.item.content_type === 'etiregistry'"
          :row="row"
          :newValue="row.item.new_obj_json.institution.name"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.institution.name : null"
          labelName="nameInstitution"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'medicalsertificate' || row.item.content_type === 'medicalcertificate'"
          :row="row"
          :newValue="row.item.new_obj_json.doctor.FIO"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.doctor.FIO : null"
          labelName="doctor"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'medicalsertificate' || row.item.content_type === 'medicalcertificate'"
          :row="row"
          :newValue="row.item.new_obj_json.doctor.medical_institution.value"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.doctor.medical_institution.value : null"
          labelName="medicalInstitution"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statementmedicalcertificate'"
          :row="row"
          :newValue="row.item.new_obj_json.medical_institution.value"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.medical_institution.value : null"
          labelName="medicalInstitution"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'studentid'"
          :row="row"
          :newValue="row.item.new_obj_json.faculty[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.faculty[langFields] : null"
          labelName="way"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'education' && row.item.new_obj_json.type_document.id === 1"
          :row="row"
          :newValue="row.item.new_obj_json.extent[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.extent[langFields] : null"
          labelName="educationExtent"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'education'"
          :row="row"
          :newValue="row.item.new_obj_json.qualification[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.qualification[langFields] : null"
          labelName="qualification"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statementadvancedtraining'"
          :row="row"
          :newValue="row.item.new_obj_json.level_qualification[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.level_qualification[langFields] : null"
          labelName="qualification"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'education' && (row.item.new_obj_json.type_document.id === 1 ||
           row.item.new_obj_json.type_document.id === 2)"
          :row="row"
          :newValue="row.item.new_obj_json.speciality[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.speciality[langFields] : null"
          labelName="specialty"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'education' && row.item.new_obj_json.type_document.id === 1"
          :row="row"
          :newValue="row.item.new_obj_json.specialization[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.specialization[langFields] : null"
          labelName="specialization"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'certificateeti'"
          :row="row"
          :newValue="row.item.new_obj_json.ntz[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.ntz[langFields] : null"
          labelName="nameInstitution"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'certificateeti'"
          :row="row"
          :newValue="row.item.new_obj_json.course_traning[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.course_traning[langFields] : null"
          labelName="qualification"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statementeti' || row.item.content_type === 'courseprice' ||
            row.item.content_type === 'etiregistry' || row.item.content_type === 'etimonthratio'"
          :row="row"
          :newValue="row.item.new_obj_json.course[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.course[langFields] : null"
          labelName="course"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'etimonthratio'"
          :row="row"
          :newValue="row.item.new_obj_json.ntz[langETI]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.ntz[langETI] : null"
          labelName="nameInstitution"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'etimonthratio'"
          :row="row"
          :newValue="row.item.new_obj_json.ratio"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.ratio : null"
          labelName="ratio"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'etimonthratio'"
          :row="row"
          :newValue="row.item.new_obj_json.month_amount"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.month_amount : null"
          labelName="monthAmount"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'medicalsertificate' || row.item.content_type === 'medicalcertificate'"
          :row="row"
          :newValue="row.item.new_obj_json.limitation[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.limitation[langFields] : null"
          labelName="limitation"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'qualitifcationdocument' || row.item.content_type === 'qualificationdocument' ||
           row.item.content_type === 'proofofworkdiploma' || row.item.content_type === 'statemenetqualificationdocument' ||
           row.item.content_type === 'sailorstatementdkk' || row.item.content_type === 'protocolsqc' ||
           row.item.content_type === 'demandpositiondkk' || row.item.content_type === 'packetitem' ||
           row.item.content_type === 'statementsqc'"
          :row="row"
          :newValue="row.item.new_obj_json.rank[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.rank[langFields] : null"
          labelName="rank"
          class="w-50"
        />
        <div
          v-if="row.item.content_type === 'qualitifcationdocument' || row.item.content_type === 'proofofworkdiploma' ||
           row.item.content_type === 'statemenetqualificationdocument' || row.item.content_type === 'sailorstatementdkk' ||
           row.item.content_type === 'demandpositiondkk' || row.item.content_type === 'protocolsqc' ||
           row.item.content_type === 'packetitem' || row.item.content_type === 'qualificationdocument' ||
           row.item.content_type === 'statementsqc'"
          class="w-50"
        >
          <div v-if="!row.item.old_obj_json">
            <label>{{ $t('position') }}:</label>
            <span v-if="row.item.content_type === 'protocolsqc' ||  row.item.content_type === 'packetitem'">
              <span v-for="position of row.item.new_obj_json.position" :key="position.id">
                {{ position[langFields] }};
              </span>
            </span>
            <span v-else>
              <span v-for="position of row.item.new_obj_json.list_positions" :key="position.id">
                {{ position[langFields] }};
              </span>
            </span>
          </div>
          <div v-else class="mb-1">
            <label>{{ $t('position') }}:</label>
            <span
              v-for="position of this.arrayDifference"
              :key="position.id"
              :class="{
                'added-record': position.status === 'added',
                'deleted-record': position.status === 'deleted',
                'exist-record': position.status === 'exists'
              }"
            >
              {{ position.name }};
            </span>
          </div>
        </div>
        <div
          v-if="row.item.content_type === 'user'"
          class="d-flex wrap w-100"
        >
          <ChangedField
            v-if="!row.item.new_obj_json.userprofile.doctor_info"
            :row="row"
            :newValue="setUserFullName('new_obj_json')"
            :oldValue="setUserFullName('old_obj_json')"
            labelName="nameUK"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.userprofile.main_group[0]"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.userprofile.main_group[0] : null"
            labelName="permissions"
            class="w-50"
          />
          <ChangedField
            v-if="row.item.new_obj_json.agent_group"
            :row="row"
            :newValue="row.item.new_obj_json.agent_group.name_ukr"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.agent_group.name_ukr : null"
            labelName="group"
            class="w-50"
          />
          <ChangedField
            v-if="row.item.new_obj_json.userprofile.doctor_info"
            :row="row"
            :newValue="row.item.new_obj_json.userprofile.doctor_info.name_ukr"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.userprofile.doctor_info.name_ukr : null"
            labelName="group"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.userprofile.branch_office"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.userprofile.branch_office : null"
            labelName="affiliate"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.userprofile.city"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.userprofile.city : null"
            labelName="city"
            class="w-50"
          />
        </div>
        <ChangedField
          v-if="row.item.content_type === 'statementagent' || row.item.content_type === 'userstatementverification'"
          :row="row"
          :newValue="setAgentFullName('new_obj_json')"
          :oldValue="setAgentFullName('old_obj_json')"
          labelName="nameUK"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statementagent'"
          :row="row"
          :newValue="row.item.new_obj_json.serial_passport"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.serial_passport : null"
          labelName="serialAndNum"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statementagent'"
          :row="row"
          :newValue="row.item.new_obj_json.tax_number"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.tax_number : null"
          labelName="taxNumber"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statementagent'"
          :row="row"
          :newValue="row.item.new_obj_json.city"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.city : null"
          labelName="city"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'medicalsertificate' || row.item.content_type === 'statementmedicalcertificate'"
          :row="row"
          :newValue="row.item.new_obj_json.position[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.position[langFields] : null"
          labelName="position"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'passport' || row.item.content_type === 'userstatementverification'"
          :row="row"
          :newValue="row.item.new_obj_json.inn"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.inn : null"
          labelName="taxNumber"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'userstatementverification'"
          :row="row"
          :newValue="row.item.new_obj_json.passport"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.passport : null"
          labelName="serialAndNum"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'userstatementverification'"
          :row="row"
          :newValue="row.item.new_obj_json.sailor_id"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.sailor_id : null"
          labelName="sailorId"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'passport'"
          :row="row"
          :newValue="dateNewValue('date')"
          :oldValue="dateOldValue('date')"
          labelName="dateStart"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'passport'"
          :row="row"
          :newValue="row.item.new_obj_json.issued_by"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.issued_by : null"
          labelName="passportIssued"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'oldname' || row.item.content_type === 'profile'"
          :row="row"
          :newValue="setFullName('new_obj_json', 'ua')"
          :oldValue="setFullName('old_obj_json', 'ua')"
          labelName="nameUK"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'oldname' || row.item.content_type === 'profile'"
          :row="row"
          :newValue="setFullName('new_obj_json', 'en')"
          :oldValue="setFullName('old_obj_json', 'en')"
          labelName="nameEN"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'profile'"
          :row="row"
          :newValue="dateNewValue('date_birth')"
          :oldValue="dateOldValue('date_birth')"
          labelName="dateBorn"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'profile'"
          :row="row"
          :newValue="row.item.new_obj_json.sex[langSex]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.sex[langSex] : null"
          labelName="sex"
          class="w-50"
        />
        <div
          v-if="row.item.content_type === 'statementagent' || row.item.content_type === 'user' ||
           row.item.content_type === 'profile'"
          class="w-100 pl-1 pr-1"
        >
          <div v-if="!row.item.old_obj_json">
            <label>{{ $t('contactInfo') }}:</label>
            <span v-if="row.item.content_type === 'statementagent' || row.item.content_type === 'profile'">
              <span v-for="contact of row.item.new_obj_json.contact_info" :key="contact.type_contact">
                <span v-if="contact.value">{{ setContactName(contact.type_contact) }}: {{ contact.value }};</span>
              </span>
            </span>
            <span v-else>
              <span v-for="contact of row.item.new_obj_json.userprofile.contact_info" :key="contact.type_contact">
                <span v-if="contact.value">{{ setContactName(contact.type_contact) }}: {{ contact.value }};</span>
              </span>
            </span>
          </div>
          <div v-else class="mb-1">
            <label>{{ $t('contactInfo') }}:</label>
            <span
              v-for="contact of this.arrayDifference"
              :key="contact.id"
            >
              <span
                v-if="contact.value"
                :class="{
                'added-record': contact.status === 'added',
                'deleted-record': contact.status === 'deleted',
                'exist-record': contact.status === 'exists'
              }"
              >
                {{ contact.type_contact }}: {{ contact.value }};
              </span>
            </span>
          </div>
        </div>
        <ChangedField
          v-if="row.item.content_type === 'servicerecord'"
          :row="row"
          :newValue="row.item.new_obj_json.auth_agent_ukr"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.auth_agent_ukr : null"
          labelName="nameUK"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'servicerecord'"
          :row="row"
          :newValue="row.item.new_obj_json.auth_agent_eng"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.auth_agent_eng : null"
          labelName="nameEN"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'sailorpassport'"
          :row="row"
          :newValue="row.item.new_obj_json.captain"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.captain : null"
          labelName="captain"
          class="w-50"
        />
        <div
          v-if="row.item.content_type === 'ntz'"
          class="d-flex wrap w-100"
        >
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.name"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.name : null"
            labelName="nameUa"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.name_abbr"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.name_abbr : null"
            labelName="nameEn"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.name_en"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.name_en : null"
            labelName="abbreviation"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.index"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.index : null"
            labelName="placeIndex"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.street"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.street : null"
            labelName="street"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.house_num"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.house_num : null"
            labelName="house"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.contract_number"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.contract_number : null"
            labelName="contractNumber"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.requsites"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.requsites : null"
            labelName="requisites"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.director_name"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.director_name : null"
            labelName="directorName"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.director_name_rodovoy"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.director_name_rodovoy : null"
            labelName="genitiveDirectorName"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.okpo"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.okpo : null"
            labelName="edrpou"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.fax"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.fax : null"
            labelName="fax"
            class="w-50"
          />
        </div>
        <ChangedField
          v-if="row.item.content_type === 'ntz' || row.item.content_type === 'userstatementverification'"
          :row="row"
          :newValue="row.item.new_obj_json.email"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.email : null"
          labelName="email"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'ntz' || row.item.content_type === 'userstatementverification'"
          :row="row"
          :newValue="row.item.new_obj_json.phone"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.phone : null"
          labelName="phoneNumber"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statementservicerecord'"
          :row="row"
          :newValue="row.item.new_obj_json.delivery.area"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.delivery.area : null"
          labelName="region"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statementservicerecord'"
          :row="row"
          :newValue="row.item.new_obj_json.delivery.city"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.delivery.city : null"
          labelName="city"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statementservicerecord'"
          :row="row"
          :newValue="row.item.new_obj_json.delivery.warehouse"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.delivery.warehouse : null"
          labelName="department"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'agentsailor' || row.item.content_type === 'statementagentsailor'"
          :row="row"
          :newValue="setAgentFullName('new_obj_json')"
          :oldValue="setAgentFullName('old_obj_json')"
          labelName="nameUK"
          class="w-50"
        />
        <div
          v-if="row.item.content_type === 'statementagentsailor'"
          class="d-flex wrap w-100"
        >
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.agent.userprofile.branch_office"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.agent.userprofile.branch_office : null"
            labelName="affiliate"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.agent.userprofile.city"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.agent.userprofile.city : null"
            labelName="city"
            class="w-50"
          />
        </div>
        <div
          v-if="row.item.content_type === 'agentsailor'"
          class="d-flex wrap w-100"
        >
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.agent.userprofile.branch_office[langFields]"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.agent.userprofile.branch_office[langFields] : null"
            labelName="affiliate"
            class="w-50"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.agent.userprofile.city.name"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.agent.userprofile.city.name : null"
            labelName="city"
            class="w-50"
          />
        </div>
        <ChangedField
          v-if="row.item.content_type === 'priceforposition' || row.item.content_type === 'courseprice'"
          :row="row"
          :newValue="row.item.new_obj_json.currency"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.currency : null"
          labelName="currencyValue"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'priceforposition' || row.item.content_type === 'courseprice'"
          :row="row"
          :newValue="setPriceForm('new_obj_json')"
          :oldValue="setPriceForm('old_obj_json')"
          labelName="form"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'courseprice' || row.item.content_type === 'packetitem'"
          :row="row"
          :newValue="row.item.new_obj_json.price"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.price : null"
          labelName="price"
          class="w-50"
        />
        <div
          v-if="row.item.content_type === 'priceforposition'"
          class="d-flex wrap w-100"
        >
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.type_document.value"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.type_document.value : null"
            labelName="typeDoc"
            class="w-100 pl-1 pr-1"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.full_price"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.full_price : null"
            labelName="coming"
            class="w-20"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.to_sqc"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.to_sqc : null"
            labelName="toSQC"
            class="w-20"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.to_qd"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.to_qd : null"
            labelName="toQD"
            class="w-20"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.to_td"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.to_td : null"
            labelName="toTD"
            class="w-20"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.to_sc"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.to_sc : null"
            labelName="toSC"
            class="w-20"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.to_agent"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.to_agent : null"
            labelName="toAgent"
            class="w-20"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.to_mrc"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.to_mrc : null"
            labelName="toMRC"
            class="w-20"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.to_medical"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.to_medical : null"
            labelName="toMedical"
            class="w-20"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.to_cec"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.to_cec : null"
            labelName="toCEC"
            class="w-20"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.to_portal"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.to_portal : null"
            labelName="toPortal"
            class="w-20"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.sum_to_distribution"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.sum_to_distribution : null"
            labelName="all"
            class="w-20"
          />
          <ChangedField
            :row="row"
            :newValue="row.item.new_obj_json.profit"
            :oldValue="row.item.old_obj_json ? row.item.old_obj_json.profit : null"
            labelName="profit"
            class="w-20"
          />
        </div>
        <ChangedField
          v-if="row.item.content_type === 'education'"
          :row="row"
          :newValue="dateNewValue('date_issue_document')"
          :oldValue="dateOldValue('date_issue_document')"
          labelName="dateStart"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'servicerecord'"
          :row="row"
          :newValue="dateNewValue('date_issued')"
          :oldValue="dateOldValue('date_issued')"
          labelName="dateStart"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'sailorpassport' || row.item.content_type === 'studentid' ||
           row.item.content_type === 'qualitifcationdocument' || row.item.content_type === 'proofofworkdiploma' ||
           row.item.content_type === 'certificateeti' || row.item.content_type === 'medicalsertificate' ||
           row.item.content_type === 'lineinservicerecord' || row.item.content_type === 'priceforposition' ||
           row.item.content_type === 'courseprice' || row.item.content_type === 'etiprofitpart' ||
           row.item.content_type === 'etiregistry' || row.item.content_type === 'medicalcertificate' ||
           row.item.content_type === 'qualificationdocument'"
          :row="row"
          :newValue="dateNewValue('date_start')"
          :oldValue="dateOldValue('date_start')"
          labelName="dateStart"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'education'"
          :row="row"
          :newValue="dateNewValue('date_end_educ')"
          :oldValue="dateOldValue('date_end_educ')"
          labelName="dateEnd"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'sailorpassport' || row.item.content_type === 'studentid' ||
           row.item.content_type === 'qualitifcationdocument' || row.item.content_type === 'proofofworkdiploma' ||
           row.item.content_type === 'certificateeti' || row.item.content_type === 'protocolsqc' ||
           row.item.content_type === 'medicalsertificate' || row.item.content_type === 'lineinservicerecord' ||
           row.item.content_type === 'priceforposition' || row.item.content_type === 'courseprice' ||
           row.item.content_type === 'etiprofitpart' || row.item.content_type === 'etiregistry' ||
           row.item.content_type === 'medicalcertificate' || row.item.content_type === 'qualificationdocument'"
          :row="row"
          :newValue="dateNewValue('date_end')"
          :oldValue="dateOldValue('date_end')"
          labelName="dateEnd"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'sailorpassport'"
          :row="row"
          :newValue="dateNewValue('date_renewal')"
          :oldValue="dateOldValue('date_renewal')"
          labelName="dateRenewal"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statementadvancedtraining' || row.item.content_type === 'statemenetqualificationdocument' ||
           row.item.content_type === 'statementeti' || row.item.content_type === 'sailorstatementdkk' ||
           row.item.content_type === 'protocolsqc' || row.item.content_type === 'statementmedicalcertificate' ||
           row.item.content_type === 'statementsqc'"
          :row="row"
          :newValue="dateNewValue('date_meeting')"
          :oldValue="dateOldValue('date_meeting')"
          labelName="dateMeeting"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statementadvancedtraining' || row.item.content_type === 'statementeti'"
          :row="row"
          :newValue="dateNewValue('date_end_meeting')"
          :oldValue="dateOldValue('date_end_meeting')"
          labelName="dateEndMeeting"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'lineinservicerecord' &&
           row.item.new_obj_json.record_type === 'Трудова книжка, довідка про фаховий стаж, ремонт, практику, тощо'"
          :row="row"
          :newValue="row.item.new_obj_json.days_work"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.days_work : null"
          labelName="totalDays"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'etiprofitpart'"
          :row="row"
          :newValue="row.item.new_obj_json.percent_of_eti"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.percent_of_eti : null"
          labelName="etiPercent"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'etiprofitpart'"
          :row="row"
          :newValue="row.item.new_obj_json.percent_of_profit"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.percent_of_profit : null"
          labelName="profitPercent"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'passport'"
          :row="row"
          :newValue="setPassportPlace('new_obj_json', 'city_registration')"
          :oldValue="setPassportPlace('old_obj_json', 'city_registration')"
          labelName="registrationDoc"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'passport'"
          :row="row"
          :newValue="setPassportPlace('new_obj_json', 'resident')"
          :oldValue="setPassportPlace('old_obj_json', 'resident')"
          labelName="residentPlace"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'qualitifcationdocument' || row.item.content_type === 'proofofworkdiploma' ||
           row.item.content_type === 'qualificationdocument'"
          :row="row"
          :newValue="row.item.new_obj_json.strict_blank"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.strict_blank : null"
          labelName="strictBlank"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'servicerecord'"
          :row="row"
          :newValue="row.item.new_obj_json.blank_strict_report"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.blank_strict_report : null"
          labelName="strictBlank"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'servicerecord'"
          :row="row"
          :newValue="row.item.new_obj_json.waibill_number"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.waibill_number : null"
          labelName="wayBillNumber"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'education'"
          :row="row"
          :newValue="row.item.new_obj_json.is_duplicate ? $t('yes') : $t('no')"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.is_duplicate ? $t('yes') : $t('no') : null"
          labelName="duplicate"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'ntz'"
          :row="row"
          :newValue="row.item.new_obj_json.is_red ? $t('yes') : $t('no')"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.is_red ? $t('yes') : $t('no') : null"
          labelName="isRed"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'etiregistry' || row.item.content_type === 'ntz'"
          :row="row"
          :newValue="row.item.new_obj_json.is_disable ? $t('yes') : $t('no')"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.is_disable ? $t('yes') : $t('no') : null"
          labelName="isDisable"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'studentid'"
          :row="row"
          :newValue="row.item.new_obj_json.educ_with_dkk ? $t('yes') : $t('no')"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.educ_with_dkk ? $t('yes') : $t('no') : null"
          labelName="educationWithSQC"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'studentid'"
          :row="row"
          :newValue="row.item.new_obj_json.educ_with_dkk ? $t('yes') : $t('no')"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.educ_with_dkk ? $t('yes') : $t('no') : null"
          labelName="passedEducationExam"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'statementsailorpassport' || row.item.content_type === 'statementadvancedtraining' ||
           row.item.content_type === 'statemenetqualificationdocument' || row.item.content_type === 'statementeti' ||
           row.item.content_type === 'sailorstatementdkk' || row.item.content_type === 'statementmedicalcertificate' ||
           row.item.content_type === 'statementservicerecord' || row.item.content_type === 'packetitem' ||
           row.item.content_type === 'statementsqc'"
          :row="row"
          :newValue="row.item.new_obj_json.is_payed ? $t('isPayed') : $t('notPayed')"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.is_payed ? $t('isPayed') : $t('notPayed') : null"
          labelName="payment"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'protocolsqc'"
          :row="row"
          :newValue="row.item.new_obj_json.decision[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.decision[langFields] : null"
          labelName="solution"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'lineinservicerecord'"
          :row="row"
          :newValue="row.item.new_obj_json.status_line[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.status_line[langFields] : null"
          labelName="status"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'servicerecord' || row.item.content_type === 'statementservicerecord'"
          :row="row"
          :newValue="row.item.new_obj_json.status[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.status[langFields] : null"
          labelName="status"
          class="w-50"
        />
        <ChangedField
          v-if="row.item.content_type === 'sailorpassport' || row.item.content_type === 'statementsailorpassport' ||
           row.item.content_type === 'education' || row.item.content_type === 'studentid' ||
           row.item.content_type === 'statementadvancedtraining' || row.item.content_type === 'qualitifcationdocument' ||
           row.item.content_type === 'proofofworkdiploma' ||
           row.item.content_type === 'certificateeti' || row.item.content_type === 'statementeti' ||
           row.item.content_type === 'sailorstatementdkk' || row.item.content_type === 'protocolsqc' ||
           row.item.content_type === 'demandpositiondkk' || row.item.content_type === 'medicalsertificate' ||
           row.item.content_type === 'statementmedicalcertificate' || row.item.content_type === 'statementagentsailor' ||
           row.item.content_type === 'statementagent' || row.item.content_type === 'userstatementverification' ||
           row.item.content_type === 'medicalcertificate' || row.item.content_type === 'qualificationdocument' ||
           row.item.content_type === 'statementsqc' || row.item.content_type === 'statemenetqualificationdocument'"
          :row="row"
          :newValue="row.item.new_obj_json.status_document[langFields]"
          :oldValue="row.item.old_obj_json ? row.item.old_obj_json.status_document[langFields] : null"
          labelName="status"
          class="w-50"
        />
      </div>
    </div>
  </b-card>
</template>

<script src="./UserHistoryInfo.js" />
