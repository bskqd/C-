<template>
  <div>
    <div class="pt-0">
      <b-card v-if="viewAdd">
        <template #header>
          <div class="flex-row-sb">
            <div class="text-uppercase">
              {{ $t(labelKeyAdd) }}
            </div>
            <unicon
              @click="viewAdd = !viewAdd"
              name="multiply"
              fill="#42627e"
              height="25px"
              width="25px"
              class="close"
            />
          </div>
        </template>
        <slot name="AddBlock"/>
      </b-card>
    </div>
    <div class="flex-row-sb">

      <SearchInTable v-model="filter"/>
      <div
        v-if="checkAccess(type, 'create') && btnAdd.includes(type)"
        @click="viewAdd = !viewAdd"
        class="col-1"
      >
        <unicon
          name="plus"
          height="30px"
          width="30px"
          class="cursor add"
        />
      </div>
    </div>

    <div
      v-if="btnMerge.includes(type) && checkAccess(type, 'merging')"
      class="d-flex justify-content-around"
    >
      <b-button
        @click="startMergingDocuments"
        variant="primary"
      >
        {{ documentMerging ? $t('stopMergingDocs') : $t('startMergingDocs') }}
      </b-button>
      <router-link
        v-if="documentMerging"
        :to="{ name: 'documents-merging', params: { sailorID: id, documents: selectedItems, type: type }}"
      >
        <b-button
          :disabled="!allowContinueMerge"
          class="bg-success text-white"
        >
          {{ $t('continueMergingDocs') }}
        </b-button>
      </router-link>
    </div>

    <b-overlay
      :show="loader"
      spinner-variant="primary"
      opacity="0.65"
      blur="2px"
      variant="white"
    >
      <b-table
        :filter="filter"
        :items="items"
        :fields="fields"
        v-model="currentItems"
        :sort-by.sync="sortBy"
        :sort-desc.sync="sortDesc"
        :responsive="true"
        :tbody-tr-class="tableRowClass"
        hover
        class="w-100"
      >
        <template #cell(selectColumn)="row">
          <b-form-checkbox
            v-model="checkedItems[row.index]"
            @input="selectDocument(row)"
            :value="true"
            :unchecked-value="false"
            :disabled="!row.item.allowMerge || (selectedItems && selectedItems.length === 2 && !checkedItems[row.index])"
          />
        </template>

        <template #head(pay_time)="data">
          <div  @click="sorting(data, 'pay_date')">
            * {{ data.label }}
            <span v-if="sortAcsBack && sortName === 'pay_date'" class="pl-25">&#11014;</span>
            <span v-if="sortDescBack && sortName === 'pay_date'" class="pl-25">&#11015;</span>
          </div>
        </template>

        <template #head(eti-course)="data">
          <div  @click="sorting(data, 'course')">
            * {{ data.label }}
            <span v-if="sortAcsBack && sortName === 'course'" class="pl-25">&#11014;</span>
            <span v-if="sortDescBack && sortName === 'course'" class="pl-25">&#11015;</span>
          </div>
        </template>
        <template #head(eti-institution)="data">
          <div  @click="sorting(data, 'institution')">
            * {{ data.label }}
            <span v-if="sortAcsBack && sortName === 'institution'" class="pl-25">&#11014;</span>
            <span v-if="sortDescBack && sortName === 'institution'" class="pl-25">&#11015;</span>
          </div>
        </template>

        <template #head(report-numberProtocol)="data">
          <div  @click="sorting(data, 'numberProtocol')">
            * {{ data.label }}
            <span v-if="sortAcsBack && sortName === 'numberProtocol'" class="pl-25">&#11014;</span>
            <span v-if="sortDescBack && sortName === 'numberProtocol'" class="pl-25">&#11015;</span>
          </div>
        </template>

        <template #head(report-dateCreated)="data">
          <div  @click="sorting(data, 'dateCreated')">
            * {{ data.label }}
            <span v-if="sortAcsBack && sortName === 'dateCreated'" class="pl-25">&#11014;</span>
            <span v-if="sortDescBack && sortName === 'dateCreated'" class="pl-25">&#11015;</span>
          </div>
        </template>

        <template #head(statement-dateCreate)="data">
          <div  @click="sorting(data, 'dateCreate')">
            * {{ data.label }}
            <span v-if="sortAcsBack && sortName === 'dateCreate'" class="pl-25">&#11014;</span>
            <span v-if="sortDescBack && sortName === 'dateCreate'" class="pl-25">&#11015;</span>
          </div>
        </template>

        <template #head(statement-status)="data">
          <div  @click="sorting(data, 'statusDocument')">
            * {{ data.label }}
            <span v-if="sortAcsBack && sortName === 'statusDocument'" class="pl-25">&#11014;</span>
            <span v-if="sortDescBack && sortName === 'statusDocument'" class="pl-25">&#11015;</span>
          </div>
        </template>

        <template #head(report-affiliate)="data">
          <div  @click="sorting(data, 'affiliate')">
            * {{ data.label }}
            <span v-if="sortAcsBack && sortName === 'affiliate'" class="pl-25">&#11014;</span>
            <span v-if="sortDescBack && sortName === 'affiliate'" class="pl-25">&#11015;</span>
          </div>
        </template>

        <template #head(report-solution)="data">
          <div  @click="sorting(data, 'solution')">
            * {{ data.label }}
            <span v-if="sortAcsBack && sortName === 'solution'" class="pl-25">&#11014;</span>
            <span v-if="sortDescBack && sortName === 'solution'" class="pl-25">&#11015;</span>
          </div>
        </template>

        <template #head(report-rank)="data">
          <div class="d-flex">
            * {{ data.label }} (
            <div class="pr-25" @click="sorting(data, 'rank')">
              {{ $t('orderABC') }}
              <span v-if="sortAcsBack && sortName === 'rank'" class="pl-25">&#11014;</span>
              <span v-if="sortDescBack && sortName === 'rank'" class="pl-25">&#11015;</span>
            </div>
            -
            <div class="pl-25" @click="sorting(data, 'rank_priority')">
              {{ $t('orderPriority') }}
              <span v-if="sortAcsBack && sortName === 'rank_priority'" class="pl-25">&#11014;</span>
              <span v-if="sortDescBack && sortName === 'rank_priority'" class="pl-25">&#11015;</span>
            </div> )
          </div>
        </template>

        <template #cell(report-sailorID)="row">
          {{ row.item.sailor && row.item.sailor.id ? row.item.sailor.id : row.item.sailor }}
        </template>

        <template #cell(report-name)="row">
          {{ row.item.recipient.last_name }} {{ row.item.recipient.first_name }} {{ row.item.recipient.middle_name }}
        </template>

        <template #cell(fullName)="row">
          {{ row.item.last_name }} {{ row.item.first_name }} {{ row.item.middle_name }}
        </template>

        <template #cell(country)="row">
          {{ row.item.country ? row.item.country[labelValue] : '' }}
        </template>

        <template #cell(report-numberProtocol)="row">
          {{ row.item.numberProtocol ? row.item.numberProtocol : '' }}
        </template>
        <template #cell(report-dateCreated)="row">
          {{ row.item.dateCreated ? row.item.dateCreated : '' }}
        </template>
        <template #cell(statement-dateCreate)="row">
          {{ row.item.date_create ? row.item.date_create : '' }}
        </template>
        <template #cell(statement-status)="row">
          <div :class="getStatus(row.item.status_document.id)">
            <span>
              {{ row.item.status_document[labelName] }}
            </span>
          </div>
        </template>
        <template #cell(report-affiliate)="row">
          {{ row.item.branch_create ? row.item.branch_create[labelName] : row.item.branch_office ? row.item.branch_office[labelName] : '' }}
        </template>
        <template #cell(is_experience_required)="row">
          {{ row.item.is_experience_required ? $t('exist') : $t('notExist') }}
        </template>
        <template #cell(sailorFullName)="row">
          {{ row.item.sailor ? row.item.sailor[`full_${labelName}`] : '' }}
        </template>
        <template #cell(report-rank)="row">
          {{ row.item.rank ? row.item.rank[labelName] : '' }}
        </template>

        <template #cell(type_document)="row">
          {{ row.item.type_document ? row.item.type_document[labelName] : '' }}
        </template>

        <template #cell(delivery)="row">
          {{ row.item.delivery ? row.item.delivery.post_service : '' }}
        </template>

        <template #cell(rank)="row">
          {{ row.item.rank ? row.item.rank[labelName] : '' }}
        </template>
        <template #cell(positionStatementRank)="row">
          {{ row.item.rank ? row.item.rank[labelName] : $t('documentApplication') }}
        </template>

        <template #cell(list_positions)="row">
          <!--{{ row.item._list_positions ? row.item._list_positions.join(', ') : '' }}-->
          <span v-for="position in row.item.list_positions" :key="position.id">
            {{ position[labelName] }};
          </span>
        </template>

        <template #cell(sqc_positions)="row">
          <span v-for="position in row.item.position" :key="position.id">
            {{ position[labelName] }};
          </span>
        </template>

        <template #cell(birthday)="row">
          {{ getDateFormat(row.item.birthday) }}
        </template>

         <template #cell(date_issue_document)="row">
          {{ getDateFormat(row.item.date_issue_document) }}
        </template>

        <template #cell(date_start)="row">
          {{ getDateFormat(row.item.date_start) }}
        </template>

        <template #cell(date_meeting)="row">
          {{ getDateFormat (row.item.date_meeting) }}
        </template>

        <template #cell(date_end_meeting)="row">
          {{ getDateFormat(row.item.date_end_meeting) }}
        </template>

        <template #cell(date_end)="row">
          {{ getDateFormat(row.item.date_end) }}
        </template>

        <template #cell(experied_date)="row">
          {{ getDateFormat(row.item.experied_date) }}
        </template>

        <template #cell(date_issued)="row">
          {{ getDateFormat(row.item.date_issued) }}
        </template>

        <template #cell(change_date)="row">
          {{ getDateFormat(row.item.change_date) }}
        </template>

        <template #cell(branch_office)="row">
          {{ row.item.branch_office ? row.item.branch_office[labelName] : '' }}
        </template>

        <template #cell(service_center)="row">
          {{ row.item.service_center ? row.item.service_center[labelName] : '' }}
        </template>

        <template #cell(includeSailorPass)="row">
          {{ row.item.includeSailorPass ? row.item.includeSailorPass[labelName] : '' }}
        </template>

        <template #cell(full_price)="row">
          {{ row.item.full_price }} <!--${$t('uah')--> {{ row.item.currency }}
        </template>
        <template #cell(positionStatementFullPrice)="row">
          {{ row.item.full_price }} {{ $t('uah') }}
        </template>

        <template #cell(qualification)="row">
            {{ row.item.qualification ? row.item.qualification[labelName] : '' }}
        </template>

        <template #cell(speciality)="row">
          {{ row.item.speciality ? row.item.speciality[labelName] : '' }}
        </template>

        <template #cell(faculty)="row">
          {{ row.item.faculty ? row.item.faculty[labelName] : '' }}
        </template>

        <template #cell(name_nz)="row">
          {{ row.item.name_nz ? row.item.name_nz[labelName] : '' }}
        </template>

        <template #cell(position)="row">
          {{ row.item.position ? row.item.position[labelName] : '' }}
        </template>

        <template #cell(limitation)="row">
          {{ row.item.limitation ? row.item.limitation[labelName] : '' }}
        </template>

        <template #cell(ntz)="row">
          {{ row.item.ntz ? row.item.ntz[labelName] : '' }}
        </template>
        <template #cell(institution)="row">
          {{ row.item.institution ? row.item.institution.name_ukr : '' }}
        </template>

        <template #cell(course_traning)="row">
          {{ row.item.course_traning ? row.item.course_traning[labelName] : '' }}
        </template>

        <template #cell(eti-course)="row">
          {{ row.item.course ? row.item.course[labelName] : '' }}
        </template>

        <template #cell(eti-institution)="row">
          {{ row.item.institution ? row.item.institution[labelName] : '' }}
        </template>

        <template #cell(course)="row">
          {{ row.item.course ? row.item.course[labelName] : '' }}
        </template>

        <template #cell(sailorPassportPort)="row">
          {{ row.item.country.id === 2 ? row.item.port[labelName] : row.item.other_port }}
        </template>
        <template #cell(qualificationStatementPort)="row">
          {{ row.item.port ? row.item.port[labelName] : '' }}
        </template>

        <template #cell(qualificationNumber)="row">
          <v-icon
            v-if="row.item.type_document.id === 16"
            style="transform: rotate(90deg)"
            large
          >
            mdi-subdirectory-arrow-left
          </v-icon>
          <span v-else>{{ row.item.number }}</span>
        </template>

        <template #cell(educational_institution)="row">
          {{ row.item.educational_institution ? row.item.educational_institution[labelName] : '' }}
        </template>

        <template #cell(level_qualification)="row">
          {{ row.item.level_qualification ? row.item.level_qualification[labelName] : '' }}
        </template>

        <template #cell(medical_institution)="row">
          {{ row.item.medical_institution ? row.item.medical_institution.value: '' }}
        </template>

        <template #cell(responsibilities)="row">
          <div v-if="row.item.record_type === 'Довідка про стаж плавання'">
            <span v-for="resp in row.item.list_responsibilities" :key="resp.responsibility.id">
              {{ resp.responsibility[labelName] }}
            </span>
          </div>
          <div v-else>
            {{ row.item.responsibility_work_book[labelName] }}
          </div>
        </template>

        <template #cell(recordBookResponsibilities)="row">
          <span v-for="resp in row.item.list_responsibilities" :key="resp.responsibility.id">
            {{ resp.responsibility[labelName] }}
          </span>
        </template>

        <template #cell(educ_with_dkk)="row">
          {{ row.item.educ_with_dkk ? $t('educationWithSQC') : $t('noEducationWithSQC') }}
        </template>

        <template #cell(passed_educ_exam)="row">
          {{ row.item.passed_educ_exam ? $t('passedEducationExam') : $t('noPassedEducationExam') }}
        </template>

        <template #cell(haveProtocol)="row">
          {{ row.item.is_have_documents.protocol ? $t('withProtocol') : $t('withoutProtocol') }}
        </template>
        <template #cell(haveStatement)="row">
          {{ row.item.is_have_documents.statement ? $t('withStatement') : $t('withoutStatement') }}
        </template>

        <template #cell(sum_to_distribution_f1)="row">
          {{ row.item.sum_to_distribution_f1.amount }}
        </template>

        <template #cell(sum_to_distribution_f2)="row">
          {{ row.item.sum_to_distribution_f2.amount }}
        </template>

        <template #cell(group)="row">
          {{ row.item.group ? row.item.group.name_ukr : '' }}
        </template>

        <template #cell(agent)="row">
          {{ row.item.agent.last_name }} {{ row.item.agent.first_name }} {{ row.item.agent.userprofile.middle_name }}
        </template>

        <template #cell(agentAffiliate)="row">
          {{ row.item.userprofile ? row.item.userprofile.branch_office : '' }}
        </template>

        <template #cell(agentCity)="row">
          {{ row.item.userprofile ? row.item.userprofile.city : '' }}
        </template>

        <template #cell(sum_f1f2)="row">
          {{ row.item.form1_sum.toFixed(2) }} ₴
          <br>
          {{ row.item.form2_sum.toFixed(2) }} $
        </template>

        <template #cell(distribution_sum)="row">
          {{ row.item.distribution_sum.toFixed(2) }}
        </template>

        <template #cell(profit_sum)="row">
          {{ row.item.profit_sum.toFixed(2) }}
        </template>

        <template #cell(is_signatured)="row">
          {{ row.item.is_signatured ? $t('signed') : $t('notSigned') }}
        </template>

        <template #cell(signature_type)="row">
          {{ $t(row.item.signature_type) }}
        </template>

        <template #cell(model)="row">
          {{ $t(row.item.model) }}
        </template>

        <template #cell(is_payed)="row">
          <div :class="getPaymentStatus(row.item.is_payed)">
            <span>
              {{ row.item.is_payed ? $t('isPayed') : $t('notPayed') }}
            </span>
          </div>
        </template>

        <template #cell(is_disable)="row">
          <div :class="getPaymentStatus(!row.item.is_disable)">
            <span>
              {{ row.item.is_disable ? $t('isDisable') : $t('isNotDisable') }}
            </span>
          </div>
        </template>

        <template #cell(is_red)="row">
          {{ row.item.is_red ? $t('yes') : $t('no') }}
        </template>

        <template #cell(type_of_form)="row">
          {{ row.item.type_of_form === 'First' ? $t('firstForm') : $t('secondForm') }}
        </template>

        <template #cell(to_sqc)="row">
          {{ row.item.to_sqc }} {{ row.item.currency }}
        </template>
        <template #cell(to_qd)="row">
          {{ row.item.to_qd }} {{ row.item.currency }}
        </template>
        <template #cell(to_td)="row">
          {{ row.item.to_td }} {{ row.item.currency }}
        </template>
        <template #cell(to_sc)="row">
          {{ row.item.to_sc }} {{ row.item.currency }}
        </template>
        <template #cell(to_agent)="row">
          {{ row.item.to_agent }} {{ row.item.currency }}
        </template>
        <template #cell(to_medical)="row">
          {{ row.item.to_medical }} {{ row.item.currency }}
        </template>
        <template #cell(to_cec)="row">
          {{ row.item.to_cec }} {{ row.item.currency }}
        </template>
        <template #cell(to_portal)="row">
          {{ row.item.to_portal }} {{ row.item.currency }}
        </template>
        <template #cell(to_mrc)="row">
          {{ row.item.to_mrc }} {{ row.item.currency }}
        </template>
        <template #cell(sum_to_distribution)="row">
          {{ row.item.sum_to_distribution }} {{ row.item.currency }}
        </template>
        <template #cell(profit)="row">
          {{ row.item.profit }} {{ row.item.currency }}
        </template>

        <template #cell(doctor)="row">
          {{ row.item.doctor ? row.item.doctor.FIO : '' }}
        </template>

        <template #cell(eti)="row">
          {{ row.item.eti ? row.item.eti[labelName] : '' }}
        </template>

        <template #cell(etiCourseName)="row">
          {{ row.item[labelName] }}
        </template>

        <template #cell(newFullName)="row">
          {{ row.item[`last_${labelName}`] }} {{ row.item[`first_${labelName}`] }} {{ row.item[`middle_${labelName}`] }}
        </template>

        <template #cell(oldFullName)="row">
          {{ row.item[`old_last_${labelName}`] }} {{ row.item[`old_first_${labelName}`] }} {{ row.item[`old_middle_${labelName}`] }}
        </template>

        <template #cell(statementDecision)="row">
          <div :class="getStatus(row.item.status_dkk.have_all_docs ? 2 : 4)">
            {{ row.item.status_dkk.have_all_docs ? $t('allowedConsideration') : $t('missingDocuments') }}
          </div>
        </template>

        <template #cell(etiInstitutionName)="row">
          {{ row.item[labelName] }}
        </template>

        <template #cell(status_document)="row">
          <div :class="getStatus(row.item.status_document.id)">
            <span>
              {{ row.item.status_document[labelName] }}
            </span>
          </div>
        </template>

        <template #cell(status_line)="row">
          <div :class="getStatus(row.item.status_line.id)">
          <span>
            {{ row.item.status_line[labelName] }}
          </span>
          </div>
        </template>

        <template #cell(decision)="row">
          <div :class="getStatus(row.item.decision ? row.item.decision.id : 5)">
          <span>
            {{ row.item.decision ? row.item.decision[labelName] : $t('waitForDecision') }}
          </span>
          </div>
        </template>

        <template #cell(protocol_status)="row">
          <div :class="getStatus(row.item.protocol_status.id)">
            <span>
              {{ row.item.protocol_status[labelName] }}
            </span>
          </div>
        </template>

        <template #cell(status)="row">
          <div :class="getStatus(row.item.status.id)">
            <span>
              {{ row.item.status[labelName] }}
            </span>
          </div>
        </template>
        <template #cell(event)="row">
          <unicon
            v-if="btnToShortInfo.includes(type)"
            @click="viewDetailedBlock(row, 'viewShortInfo') + showDetailed(row)"
            name="book-open"
            height="20px"
            width="20px"
            fill="#42627e"
            class="cursor mr-4"
          />

          <router-link
            v-if="btnToSailor.includes(type) && ((row.item.sailor && row.item.sailor.id) || row.item.sailor || row.item.sailor_id)"
            :to="{ name: 'sailor', params: { id: row.item.sailor && row.item.sailor.id ? row.item.sailor.id : row.item.sailor || row.item.sailor_id }}"
            target="_blank"
          >
            <unicon
              name="user-circle"
              height="20px"
              width="20px"
              fill="#42627e"
              class="cursor mr-4"
            />
          </router-link>

          <router-link
            v-if="!btnToSailorDocument.includes(type)"
            :to="{ name: link, params: { documentID: row.item.service_record || row.item.id, lineID: row.item.id }}"
          >
            <unicon
              name="arrowRight"
              height="20px"
              width="20px"
              fill="#42627e"
              class="cursor mr-4"
              id="tooltip"
            />
          </router-link>
          <Popover
            v-if="!btnToSailorDocument.includes(type) && row.index === 0 && !isTrained"
            :text="$t('trainingTip')"
          />

          <router-link
            v-if="btnToDocumentWithSailorId.includes(type)"
            :to="{
              name: link || row.item.link,
              params: { id: row.item.sailor && row.item.sailor.id ? row.item.sailor.id : row.item.sailor,
               documentID: row.item.service_record || row.item.id, lineID: row.item.id }}"
            target="_blank"
          >
            <unicon
              name="arrowRight"
              height="20px"
              width="20px"
              fill="#42627e"
              class="cursor mr-4"
            />
          </router-link>

          <router-link
            v-if="btnToReport.includes(type)"
            :to="{ path: `${row.item.link}`, query: { search: `${row.item.searchParams}` }}"
            target="_blank">
            <unicon
              name="info-circle"
              height="20px"
              width="20px"
              fill="#42627e"
              class="cursor mr-4"
            />
          </router-link>

          <unicon
            v-if="type === 'reportExcel' || (row.item.allowSaveExcel && type === 'reportDistributionGroup')"
            @click="saveExcel(row)"
            name="file-upload-alt"
            height="20px"
            width="20px"
            fill="#42627e"
            class="cursor mr-4"
          />

          <unicon
            v-if="btnInfo.includes(type)"
            @click="viewDetailedBlock(row, 'viewInfoBlock') + showDetailed(row)"
            fill="#42627e"
            height="20px"
            width="20px"
            class="cursor mr-4"
            name="info-circle"/>

          <unicon
            v-if="btnEdit.includes(type) && checkAccess(type, 'edit', row)"
            @click="viewDetailedBlock(row, 'viewEditBlock') + showDetailed(row)"
            name="pen"
            fill="#42627e"
            height="20px"
            width="20px"
            class="cursor mr-4"
          />

          <unicon
            v-if="btnDelete.includes(type) && checkAccess(type, 'delete', row)"
            @click="deleteRow(row)"
            name="multiply"
            fill="#42627e"
            height="20px"
            width="20px"
            class="cursor delete"
          />
        </template>

        <template #row-details="row">
          <component
            v-if="row.item.behavior.viewInfoBlock"
            :is="componentInfo"
            :row="row"
            :getDocuments="getDocuments"
            name="Info" />

          <component
            v-else-if="row.item.behavior.viewEditBlock"
            :is="componentEdit"
            :row="row"
            :getDocuments="getDocuments"
            name="Edit" />

          <component
            v-else-if="row.item.behavior.viewEditStatusBlock"
            :is="componentStatus"
            :row="row"
            :getDocuments="getDocuments"
            name="EditStatus" />

          <component
            v-else-if="row.item.behavior.viewFilesBlock"
            :is="componentFiles"
            :row="row"
            :getDocuments="getDocuments"
            name="Files" />

          <component
            v-else-if="row.item.behavior.viewShortInfo"
            :is="componentShortInfo"
            :row="row"
            name="ShortInfo" />
        </template>
      </b-table>
    </b-overlay>
  </div>
</template>

<script src="./Table.js"/>
