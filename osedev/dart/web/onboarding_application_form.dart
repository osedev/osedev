import 'dart:html';

FieldSetElement parentFieldSet(child) {
    while (true) {
        if (child is FieldSetElement) return child;
        child = child.parent;
    }
}

main() {
    Map<String,Map<String,String>> help_lookup = {};
    TemplateElement steps_data = querySelector('template#steps-help');
    steps_data.content.children.forEach((div) {
        var values = help_lookup[div.dataset['name']] = {};
        div.children.forEach((item) {
            values[item.classes.first] = item.innerHtml;
        });
    });
    querySelector('#steps-group').addEventListener('change', (event) {
        SelectElement select = event.target;
        var help = help_lookup[select.value];
        var fieldset = parentFieldSet(select);
        fieldset.querySelector('.field-instructions .help').setInnerHtml(help['instructions_help']);
        fieldset.querySelector('.field-instructions textarea').setInnerHtml(help['instructions_default']);
        fieldset.querySelector('.field-widget_conf .help').setInnerHtml(help['widget_conf_help']);
        fieldset.querySelector('.field-widget_conf textarea').setInnerHtml(help['widget_conf_default']);
    });
}
