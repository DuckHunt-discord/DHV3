<?php


require_once 'vendor/autoload.php';
$servername = "localhost";
$dbname   = "DHV3";
$username   = "duckhunt_web";
$password   = "duckhunt_web";

$admins = array(
    138751484517941259, // Eyesofcreeper#0001
);
$bug_hunters = array(
    282268617725444097, // 187#3643
    375268465097048064, // Charlie(Raptoreum)#2132
    385635006493753346, // Natedog277#0684
    624586069186314261, // Semedac#2465
    251996890369884161, // Subtleknifewielder#1927
    135446225565515776, // Taoshi#0001
    618490907578073099, // XQuicksilver_Lis#6387
);
$donators = array(
    231196637874225152, // Dany#7189
    111681841034973184, // MalcolmHimself#7415
    327841341432397824, // MsButton#9987
    135446225565515776, // Taoshi#0001
    384202884553768961, // greywolf#9207
    174585686945562624, // o_be_one#1337
);
$enigma_event_winners_june_2018 = array(
    132695220297924608, // BanditB17#2110
    276412993972207626, // Bigael#3857
    301918971274199041, // CampFire#6670
    231196637874225152, // Dany#7189
    134119746118352906, // DeafieTechie#0056
    343891647785992193, // Missiwiss#8058
    135446225565515776, // Taoshi#0001
    269910487133716480, // Toafu#4965
    248904069840764938, // boshaus#9999
    325434800192225290, // pokki#1490
);
$enigma_event_winners_november_2019 = array(
    316788628476919808, // Ahuman#8933
    387048786263801856, // ImBeyondDarkness#4070
    135446225565515776, // Taoshi#0001
    419238591248465930, // cyalknight#7736
);
$moderators = array(
    183273311503908864, // Olpouin#6797
    181846573351829504, // PierrePV#3537
    251996890369884161, // Subtleknifewielder#1927
    135446225565515776, // Taoshi#0001
    300247046856900629, // Wolterhon#3938
    380118196742651906, // rulebritannia 🇬🇧#6894
);
$partners = array(
    193879234379382784, // Daxter#6538
    120193744707256320, // Dr Zachary Smith#9260
    174585686945562624, // o_be_one#1337
);
$proficients = array(
    316788628476919808, // Ahuman#8933
    329940268457525249, // Deathclaw#0966
    231117724317646849, // Heroesflorian#4385
    273798408186363905, // InigoMontoya#9392
    251996890369884161, // Subtleknifewielder#1927
    135446225565515776, // Taoshi#0001
    191602541534904321, // Volcanard#4242
    380118196742651906, // rulebritannia 🇬🇧#6894
    174670292994621440, // sholan#0922
);
$translators = array(
    467027285229174804, // 8-Ball#1862
    286806848693338112, // Aragogne#0806
    236187090881085440, // Areisp#2416
    151016183401938944, // Crumble_#8877
    239491845237899264, // Dannysaysyolo73#0812
    297391115890589699, // El Chefe#6666
    194455213770276864, // Foxy-the-edagunCZ#1026
    338362273376501770, // G-Man#3131
    462726976763854864, // Ganny#0879
    331319593681289216, // ImparuZ#4007
    207597032792260609, // KaySteR#9760
    278599626922131459, // Legolas#2139
    350397621027864576, // Lord DréByte#2222
    214345196207341572, // Max Mustermann#0815
    549911100980723714, // Nash#4302
    510711951035465728, // PixelPirate#9172
    437737826575187980, // PurplePoisonRose1987#4048
    263216424737046528, // SlimyMelon#5435
    135446225565515776, // Taoshi#0001
    300247046856900629, // Wolterhon#3938
    193431551034392576, // barnabinnyu#9928
    202979770235879427, // estudiante#6170
    606567327311593484, // gladiarray#5346
    305771483865546752, // imLuke#2795
    211888559735570433, // pun1sher#1165
    520228168209137684, // xarthur#9599
    225383218113675264, // ⎝⧹꧁C R I S T I A N꧂⧸⎠#7926
);

$retired_staff                  = array(
    94822638991454208,  // Diagamma#7456
    296573428293697536, // ʳᵉᵛⁱᵛⁱⁿᵍ⚜Wizzz⚜#7777
);


try {
    $conn = new PDO("mysql:host=$servername;dbname=$dbname;charset=utf8mb4", $username, $password);
    // set the PDO error mode to exception
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    //echo "Connected successfully";
}
catch (PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
    die;
}


if (isset($_GET['cid'])) {
    $channel_id   = (int)$_GET['cid'];
    $db_cid_query = $conn->prepare("SELECT id, channel_name FROM channels WHERE channel=:channel_id");
    $db_cid_query->bindParam(':channel_id', $channel_id);
    $db_cid_query->setFetchMode(PDO::FETCH_ASSOC);
    $db_cid_query->execute();
    $db_c            = $db_cid_query->fetch();
    $db_channel_id   = $db_c['id'];
    $db_channel_name = $db_c['channel_name'];

    if (isset($_GET['pid'])) { // On a la channel et le player

        $player_id          = (int)$_GET['pid'];
        $player_stats_query = $conn->prepare("SELECT * FROM players WHERE channel_id=:channel_id and id_=:player_id LIMIT 1");
        $player_stats_query->bindParam(':channel_id', $db_channel_id);
        $player_stats_query->bindParam(':player_id', $player_id);
        $player_stats_query->setFetchMode(PDO::FETCH_ASSOC);
        $player_stats_query->execute();

        if ($player_stats_query->rowCount() == 0) {
            http_response_code(404);
            die("Player or channel not found!");
        }

        $player_stats = $player_stats_query->fetch();


        //print_r($player_stats);

        $player_stats['channel_name'] = $db_channel_name;
        $player_stats['channel_id']   = $channel_id;

        $player_stats['badges'] = array(
            "banned"                        => $player_stats['banned'],
            "no_weapon"                     => (time() - $player_stats['confiscated']) < 0,
            "admin"                         => in_array($player_stats['id_'], $admins),
            "moderator"                     => in_array($player_stats['id_'], $moderators),
            "translator"                    => in_array($player_stats['id_'], $translators),
            "bug_hunter"                    => in_array($player_stats['id_'], $bug_hunters),
            "proficient"                    => in_array($player_stats['id_'], $proficients),
            "retired_staff"                 => in_array($player_stats['id_'], $retired_staff),
            "partner"                       => in_array($player_stats['id_'], $partners),
            "donator"                       => in_array($player_stats['id_'], $donators),
            "enigma_event_winner_june_2018" => in_array($player_stats['id_'], $enigma_event_winners_june_2018),
        );

        $player_stats['achievements'] = array(
            "time_played_1"  => $player_stats['givebacks'] > 7,
            "time_played_2"  => $player_stats['givebacks'] > 30,
            "clueless"       => $player_stats['exp'] < -15,
            "scientist"      => $player_stats['exp'] > 2090,
            "max_level"      => $player_stats['exp'] > 11111,
            "cheater"        => $player_stats['exp'] > 1000000,
            "baby_lover"     => $player_stats['killed_baby_ducks'] < 5,
            "murderer"       => $player_stats['murders'] > 0,
            "first_blood"    => $player_stats['killed_ducks'] > 1,
            "ducks_killed_1" => $player_stats['killed_ducks'] > 10,
            "ducks_killed_2" => $player_stats['killed_ducks'] > 100,
            "ducks_killed_3" => $player_stats['killed_ducks'] > 500,
            "ducks_killed_4" => $player_stats['killed_ducks'] > 1000,
            "ducks_killed_5" => $player_stats['killed_ducks'] > 2000,
            "ducks_killed_6" => $player_stats['killed_ducks'] > 4000,
            "lucky_user"     => $player_stats['exp_won_with_clover'] > 500,

        );


        if (isset($_GET['api-agent'])){
            header('Content-Type: application/json');
            echo json_encode($player_stats, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_NUMERIC_CHECK);
            die();
        } else {
            $loader = new Twig_Loader_Filesystem('templates');

            $twig = new Twig_Environment($loader, array(//'cache' => 'cache',
            ));
            $twig->addExtension(new \Snilius\Twig\SortByFieldExtension());

            echo $twig->render('duckstats_player.twig', $player_stats);
            die();
        }




    } else {
        // Player not passed, displaying chan statistics
        $players_array_query = $conn->prepare("SELECT * FROM players WHERE channel_id=:channel_id AND (exp <> 0 OR killed_ducks > 0) ORDER BY exp DESC");
        $players_array_query->bindParam(':channel_id', $db_channel_id);
        $players_array_query->setFetchMode(PDO::FETCH_ASSOC);
        $players_array_query->execute();

        if ($players_array_query->rowCount() == 0) {
            http_response_code(404);
            die("Channel not found!");
        }

        $players_array = $players_array_query->fetchall();


        $total_normal_ducks     = 0;
        $total_super_ducks      = 0;
        $total_baby_ducks       = 0;
        $total_moad_ducks       = 0;
        $total_mechanical_ducks = 0;
        $total_players_killed   = 0;


        foreach ($players_array as &$player) {
            $total_normal_ducks     += $player['killed_normal_ducks'];
            $total_super_ducks      += $player['killed_super_ducks'];
            $total_baby_ducks       += $player['killed_baby_ducks'];
            $total_moad_ducks       += $player['killed_mother_of_all_ducks'];
            $total_mechanical_ducks += $player['killed_mechanical_ducks'];
            $total_players_killed   += $player['killed_players'];
        }


        $passed = [
            "players"                => $players_array,
            "channel_name"           => $db_channel_name,
            "channel_id"             => $channel_id,
            "total_normal_ducks"     => $total_normal_ducks,
            "total_super_ducks"      => $total_super_ducks,
            "total_baby_ducks"       => $total_baby_ducks,
            "total_moad_ducks"       => $total_moad_ducks,
            "total_mechanical_ducks" => $total_mechanical_ducks,
            "total_players_killed"   => $total_players_killed,
        ];


        if (isset($_GET['api-agent'])){
            header('Content-Type: application/json');
            $passed["players"] = array_values($passed["players"]);
            echo json_encode($passed, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_NUMERIC_CHECK);
            die();
        } else {
            $loader = new Twig_Loader_Filesystem('templates');

            $twig = new Twig_Environment($loader, array(//'cache' => 'cache',
            ));
            $twig->addExtension(new \Snilius\Twig\SortByFieldExtension());

            echo $twig->render('duckstats_channel.twig', $passed);
            die();
        }



    }


} else // Il manque des paramètres, RIP

{

    header("Location: .", true, 301);
    die();

}
