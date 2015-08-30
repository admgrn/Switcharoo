var push = true;
var offset = 350 / 2;

var ContentLoading = {
    show: function () {
        $('#loading-content').show();
        $('#selected-content').hide();
    },
    hide: function () {
        $('#loading-content').hide();
        $('#selected-content').show();
    }
};
var FormSuccess = {
    show: function (location) {
        $('.submit-success-' + $(location).find('input[name=type]').val()).css('display','');
        $(location).removeClass('uk-display-inline-block');
        $(location).css('display', 'none');
    },
    hide: function (location) {
        $('.submit-success-' + $(location).find('input[name=type]').val()).css('display','none');
        $(location).addClass('uk-display-inline-block');
        $(location).css('display', '');
    }
};
function hideMainLoading() {
    $('#loading-main').hide();
}
function decodeHtml(html) {
    var txt = document.createElement("textarea");
    txt.innerHTML = html;
    return txt.value;
}
function getTime(timestamp) {
    var d = new Date(timestamp * 1000);
    return d.toLocaleDateString() + " " + d.toLocaleTimeString();
}
function displayError(id) {
    $('#display-error-' + id).css('display', '')
}
function state(location, id, replace) {
    if (!replace)
        history.pushState({loc: location, id: id}, '', location);
    else
        history.replaceState({loc: location, id: id}, '', location);
}
function showInfo(params, callback, updateState) {
    var id = typeof params === 'number' ? params : params.nodes[0];
    ContentLoading.show();
    $.ajax('/get_info/' + id)
            .done(function (data) {
                if (data.success) {
                    $('#selected-info').text(data.title);
                    $('#selected-link').attr('href', data.link);
                    $('#selected-html').html(decodeHtml(data.html));
                    $('#selected-html a[href]').attr('target', '_blank');
                    if (data.user !== null)
                        $('#username').text('/u/' + data.user)
                            .css('font-style', '')
                            .attr('href', 'https://reddit.com/u/' + data.user);
                    else
                        $('#username').text('[deleted]')
                            .css('font-style', 'italic')
                            .attr('href', 'javascript:void(0)');
                    $('#created-date').text('Submitted: ' + getTime(data.date));
                    if (updateState)
                        state('/location/' + data.id, data.id);
                    callback(true);
                } else {
                    if (updateState)
                        state('/');
                    callback(false);
                }
                ContentLoading.hide();
            });
    UIkit.offcanvas.show('#left-canvas');
}
function checkUrl() {
    var id;
    if ((id = window.location.href.match(/\/location\/(\d+)/)) !== null)
        id = parseInt(id[1]);
    return id;
}

$(function () {
    // Create network
    var nodes = new vis.DataSet();
    var edges = new vis.DataSet();
    var container = document.getElementById('graph-navigator');
    var data = {
        nodes: nodes,
        edges: edges
    };
    var options = {
        edges: {
            arrows: {
                to: {
                    enabled: true,
                    scaleFactor: 2.5
                }
            },
            smooth: {
                enabled: false
            },
            color: 'rgb(100,100,100)'
        },
        nodes: {
            borderWidth: 0.8,
            shape: 'circle',
            font: {
                size: 50
            },
            scaling : {
                min: 300
            }
        },
        layout: {
            randomSeed: 1
        },
        physics: {
            enabled: true,
            stabilization: false,
            barnesHut: {
                centralGravity: 0,
                springConstant: 0,
                springLength: 0,
                avoidOverlap: 1,
                damping: 0.3
            }
        }
    };

    var network = new vis.Network(container, data, options);
    network.on('selectNode', function (e) {
        showInfo(e, function (success) {
            if (success) {
                network.selectNodes([e.nodes[0]], true);
                network.focus(e.nodes[0], {
                    animation: {
                        duration: 200
                    },
                    offset: {
                        x: -offset
                    }
                });
            }
        }, true);
    });

    // Load content
    $.ajax('/load_content')
        .done(function (content) {
                var id;
                if ((id = checkUrl()) !== null) {
                    showInfo(id, function (success) {
                        nodes.add(content['nodes']);
                        edges.add(content['relations']);
                        if (success) {
                            state('/location/' + id, id, true);
                            network.selectNodes([id], true);
                            network.focus(id, {
                                offset: {
                                    x: -offset
                                }
                            });
                        } else {
                            state('/location/' + id, id, true);
                            network.fit();
                        }
                        hideMainLoading();
                    });
                } else {
                    nodes.add(content['nodes']);
                    edges.add(content['relations']);
                    state('/', null, true);
                    network.fit();
                    hideMainLoading();
                }
        });

    // Set Validations
    $('.async-form').each(function () {
        $(this).validate({
            rules: {
                email: {
                    required: true,
                    email: true
                }
            },
            errorPlacement: function (error, element) {
                $(error).addClass('uk-form-help-block');
                $(element).parent().append(error);
            },
            highlight: function (element) {
                $(element).addClass('uk-form-danger');
            },
            unhighlight: function (element) {
                $(element).removeClass('uk-form-danger');
            },
            submitHandler: function (form) {
                $(form).find('.submit-button').attr('disabled', 'disabled');
                var name = $(form).find('input[name=type]').val();
                var location = '/api/' + name + '/';
                var formData = $(form).serialize();
                $.post(location, formData, function (resp) {
                    if (resp === 'GOOD') {
                        FormSuccess.show(form);
                        $(form).find('.clear-done').val('');
                    } else {
                        displayError(name);
                    }
                })
                .always(function () {
                    $(form).find('.submit-button').removeAttr('disabled');
                });
                return false;
            }
        });
    });

    // Event handlers
    $('.uk-modal').on('hide.uk.modal', function () {
        $(this).find('[id^=display-error-]').css('display', 'none');
        FormSuccess.hide($(this).find('.async-form'));
    });
    $('#left-canvas').on('hide.uk.offcanvas', function () {
        network.moveTo({
            offset: {
                x: offset
            },
            animation: {
                duration: 100
            }
        });
        if (push)
            state('/');
        else
            push = true;
    });
    $(window).on('popstate', function (e) {
        if (e.originalEvent.state.id) {
            var id = parseInt(e.originalEvent.state.id);
            showInfo(id, function (success) {
                if (success) {
                    network.selectNodes([id], true);
                    network.focus(id, {
                        animation: {
                            duration: 200
                        },
                        offset: {
                            x: -offset
                        }
                    });
                }
            });
        } else {
            push = false;
            UIkit.offcanvas.hide();
        }
    });
});