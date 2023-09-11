const PromptsEditorField = {
    props: [
        'modelValue',
        'title',
        'editablePrompt',
    ],
    emits: ['update:modelValue'],
    data() {
        return {
            showEditor: false,
            MAX_VALUES: 256,
            loading: false,
        }
    },
    methods: {
        updateField({ target: { value }}) {
            this.$emit('update:modelValue', value);
        },
        openEditDesc() {
            this.showEditor = !this.showEditor;
        },
        saveDesc() {
            if (this.hasError(this.modelValue)) {
                return;
            }
            this.loading = true;
            ApiUpdatePrompt(this.editablePrompt).then(data => {
                this.$emit('update:modelValue', this.modelValue.trim());
                showNotify('SUCCESS', `${this.title} updated.`);
                this.showEditor = false;
            }).finally(() => {
                this.loading = false;
            });
        },
        hasError(value) {
            return value.length > this.MAX_VALUES;
        },
    },
    template: `
        <div class="mb-3">
            <div class="d-flex flex-column align-items-start">
                <p class="font-h6 font-bold font-uppercase text-gray-700 mb-1">{{ title }}</p>
                <div class="d-flex justify-content-between" v-if="!showEditor">
                    <span class="mr-2">{{ modelValue }}</span>
                    <button type="button"
                        style="min-width: 24px"
                        class="btn btn-default btn-xs btn-table btn-icon__xs edit_user" 
                        @click="openEditDesc" 
                        data-toggle="tooltip" 
                        data-placement="top">
                        <i class="icon__18x18 icon-edit"></i>
                    </button>
                </div>
            </div>
            <div v-if="showEditor" class="d-flex justify-content-end align-items-center">
                <div class="custom-input flex-grow-1 need-validation":class="{'invalid-input': hasError(modelValue)}"
                    :data-valid="hasError(modelValue)">
                    <textarea rows="2" class="form-control" 
                    :value="modelValue" @input="updateField">{{ modelValue }}</textarea>
                    <span class="input_error-msg font-h6 font-weight-400 text-right">{{ modelValue.length }}/256</span>
                </div>
                <button class="btn btn-success__custom btn-xs btn-icon__xs ml-2" @click="saveDesc">
                    <i class="preview-loader__white" v-if="loading"></i>
                    <i v-else class="icon__16x16 icon-check__white"></i>
                </button>
            </div>   
        </div> 
        
    `
}