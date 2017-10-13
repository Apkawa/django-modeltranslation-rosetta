'use strict';
import $ from 'jquery'

$(() => {
    $('.copy_to_right').on('click', function () {
        const $el = $(this);
        // TODO проверить на случай с несколькими языками
        const $left = $el.parent().prev().find(':input');
        const $right = $el.parent().next().find(':input');
        if (window.tinyMCE !== undefined) {
            const mce_left = window.tinyMCE.get($left.attr('id'));
            const mce_right = window.tinyMCE.get($right.attr('id'));
            if (mce_left) {
                mce_right.setContent(mce_left.getContent())
                return
            }
        }
        if ($right[0].redactor) {
            // ugly hacks
            $right[0].redactor('code.set', $left.val())
            return
        }
        $right.val($left.val());
    })
})