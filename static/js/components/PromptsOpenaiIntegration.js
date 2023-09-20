const PromptsOpenaiIntegration = {
    props: ['selectedPrompt', 'isRunClicked', 'selectedIntegration'],
    components: {
        'prompts-range': PromptsRange,
    },
    data() {
        return {
            editableIntegrationSetting: {
                temperature: 0,
                max_tokens: 1,
                top_p: 0,
                model: ""
            },
            isComponentMounted: false,
        }
    },
    computed: {
        responsiveTableHeight() {
            return `${(window.innerHeight - 270)}px`;
        },
        isInvalid() {
            return this.isRunClicked && !this.editableIntegrationSetting.model_name
        }
    },
    mounted() {
        if (this.selectedPrompt.model_settings) {
            this.editableIntegrationSetting = { ...this.selectedPrompt.model_settings };
            this.isComponentMounted = true;
        }
        this.$nextTick(() => {
            $('#selectModel').val(this.editableIntegrationSetting.model_name).selectpicker('refresh');
        })
    },
    watch: {
        editableIntegrationSetting: {
            handler: function (newVal, oldVal) {
                this.$emit('update-setting', newVal)
            },
            deep: true
        }
    },
    template: `
        <div>
            <div class="mt-4" v-if="isComponentMounted">
            <div class="select-validation mt-4 mb-4" :class="{ 'invalid-input': isInvalid }">
                <p class="font-h5 font-semibold mb-1">Select model</p>
                <select id="selectModel" class="selectpicker bootstrap-select__b bootstrap-select__b-sm"
                    v-model="editableIntegrationSetting.model_name"
                    data-size="8"
                    data-style="btn">
                    <option v-for="model in selectedIntegration.settings.models" :value="model">{{ model }}</option>
                </select>
            </div>
                </div>
                <prompts-range
                    @register="$root.register"
                    instance_name="prompts-range"
                    title="temperature"
                    :step="0.05"
                    :minValue="0"
                    :maxValue="1"
                    v-model:modelValue="editableIntegrationSetting.temperature"
                ></prompts-range>
                <prompts-range
                    @register="$root.register"
                    instance_name="prompts-range"
                    title="Token limit"
                    :step="1"
                    :minValue="1"
                    :maxValue="32000"
                    v-model:modelValue="editableIntegrationSetting.max_tokens"
                ></prompts-range>
                <prompts-range
                    @register="$root.register"
                    instance_name="prompts-range"
                    title="Top-P"
                    :step="0.05"
                    :minValue="0"
                    :maxValue="1"
                    v-model:modelValue="editableIntegrationSetting.top_p"
                ></prompts-range>
            </div>
        </div>
    `
}
